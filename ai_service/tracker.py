"""
SORT (Simple Online and Realtime Tracking) Implementation.
Based on the original SORT paper by Bewley et al.

Tracks detected vehicles across frames using Kalman Filter
and Hungarian Algorithm for data association.
"""

import numpy as np
from filterpy.kalman import KalmanFilter
from scipy.optimize import linear_sum_assignment


def iou(bb_test: np.ndarray, bb_gt: np.ndarray) -> float:
    """
    Calculate Intersection over Union (IoU) between two bounding boxes.
    
    Args:
        bb_test: Bounding box [x1, y1, x2, y2]
        bb_gt: Ground truth bounding box [x1, y1, x2, y2]
    
    Returns:
        IoU value between 0 and 1
    """
    xx1 = np.maximum(bb_test[0], bb_gt[0])
    yy1 = np.maximum(bb_test[1], bb_gt[1])
    xx2 = np.minimum(bb_test[2], bb_gt[2])
    yy2 = np.minimum(bb_test[3], bb_gt[3])

    w = np.maximum(0.0, xx2 - xx1)
    h = np.maximum(0.0, yy2 - yy1)
    intersection = w * h

    area_test = (bb_test[2] - bb_test[0]) * (bb_test[3] - bb_test[1])
    area_gt = (bb_gt[2] - bb_gt[0]) * (bb_gt[3] - bb_gt[1])

    union = area_test + area_gt - intersection
    return intersection / union if union > 0 else 0.0


def convert_bbox_to_z(bbox: np.ndarray) -> np.ndarray:
    """Convert [x1, y1, x2, y2] to [cx, cy, area, aspect_ratio]."""
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    cx = bbox[0] + w / 2.0
    cy = bbox[1] + h / 2.0
    area = w * h
    ratio = w / float(h) if h > 0 else 1.0
    return np.array([cx, cy, area, ratio]).reshape((4, 1))


def convert_z_to_bbox(z: np.ndarray) -> np.ndarray:
    """Convert [cx, cy, area, aspect_ratio] to [x1, y1, x2, y2]."""
    w = np.sqrt(z[2] * z[3])
    h = z[2] / w if w > 0 else 0
    return np.array([
        z[0] - w / 2.0,
        z[1] - h / 2.0,
        z[0] + w / 2.0,
        z[1] + h / 2.0,
    ]).reshape((1, 4))


class KalmanBoxTracker:
    """
    Represents the internal state of a tracked object using Kalman Filter.
    State vector: [cx, cy, area, ratio, vx, vy, va]
    """
    count = 0

    def __init__(self, bbox: np.ndarray):
        """Initialize tracker with initial bounding box."""
        self.kf = KalmanFilter(dim_x=7, dim_z=4)
        
        # State transition matrix
        self.kf.F = np.array([
            [1, 0, 0, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 1, 0],
            [0, 0, 1, 0, 0, 0, 1],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 1],
        ])

        # Measurement matrix
        self.kf.H = np.array([
            [1, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
        ])

        # Measurement noise
        self.kf.R[2:, 2:] *= 10.0
        # Covariance matrix
        self.kf.P[4:, 4:] *= 1000.0
        self.kf.P *= 10.0
        # Process noise
        self.kf.Q[-1, -1] *= 0.01
        self.kf.Q[4:, 4:] *= 0.01

        self.kf.x[:4] = convert_bbox_to_z(bbox)

        self.time_since_update = 0
        self.id = KalmanBoxTracker.count
        KalmanBoxTracker.count += 1
        self.history = []
        self.hits = 0
        self.hit_streak = 0
        self.age = 0
        
        # Track position history for speed estimation
        self.positions = [(self.kf.x[0, 0], self.kf.x[1, 0])]

    def update(self, bbox: np.ndarray):
        """Update the tracker with a new detection."""
        self.time_since_update = 0
        self.history = []
        self.hits += 1
        self.hit_streak += 1
        self.kf.update(convert_bbox_to_z(bbox))
        self.positions.append((self.kf.x[0, 0], self.kf.x[1, 0]))
        
        # Keep last 30 positions for speed calculation
        if len(self.positions) > 30:
            self.positions = self.positions[-30:]

    def predict(self) -> np.ndarray:
        """Predict the next state."""
        if (self.kf.x[6] + self.kf.x[2]) <= 0:
            self.kf.x[6] *= 0.0

        self.kf.predict()
        self.age += 1

        if self.time_since_update > 0:
            self.hit_streak = 0

        self.time_since_update += 1
        self.history.append(convert_z_to_bbox(self.kf.x))
        return self.history[-1]

    def get_state(self) -> np.ndarray:
        """Get current bounding box estimate."""
        return convert_z_to_bbox(self.kf.x)

    def get_speed_pixels_per_frame(self) -> float:
        """Estimate speed in pixels per frame from position history."""
        if len(self.positions) < 2:
            return 0.0
        
        recent = self.positions[-5:]  # Last 5 positions
        total_displacement = 0.0
        for i in range(1, len(recent)):
            dx = recent[i][0] - recent[i - 1][0]
            dy = recent[i][1] - recent[i - 1][1]
            total_displacement += np.sqrt(dx**2 + dy**2)
        
        return total_displacement / (len(recent) - 1)


def associate_detections_to_trackers(
    detections: np.ndarray,
    trackers: np.ndarray,
    iou_threshold: float = 0.3,
) -> tuple:
    """
    Associate detections to tracked objects using IoU and Hungarian algorithm.
    
    Returns:
        matches: Array of matched [detection_idx, tracker_idx] pairs
        unmatched_detections: Array of unmatched detection indices
        unmatched_trackers: Array of unmatched tracker indices
    """
    if len(trackers) == 0:
        return (
            np.empty((0, 2), dtype=int),
            np.arange(len(detections)),
            np.empty((0,), dtype=int),
        )

    if len(detections) == 0:
        return (
            np.empty((0, 2), dtype=int),
            np.empty((0,), dtype=int),
            np.arange(len(trackers)),
        )

    # Build IoU cost matrix
    iou_matrix = np.zeros((len(detections), len(trackers)), dtype=np.float32)
    for d, det in enumerate(detections):
        for t, trk in enumerate(trackers):
            iou_matrix[d, t] = iou(det, trk)

    # Hungarian algorithm (minimize cost = maximize IoU)
    row_indices, col_indices = linear_sum_assignment(-iou_matrix)

    matched_indices = np.column_stack((row_indices, col_indices))

    unmatched_detections = [d for d in range(len(detections)) if d not in matched_indices[:, 0]]
    unmatched_trackers = [t for t in range(len(trackers)) if t not in matched_indices[:, 1]]

    # Filter out low IoU matches
    matches = []
    for m in matched_indices:
        if iou_matrix[m[0], m[1]] < iou_threshold:
            unmatched_detections.append(m[0])
            unmatched_trackers.append(m[1])
        else:
            matches.append(m.reshape(1, 2))

    if len(matches) == 0:
        matches = np.empty((0, 2), dtype=int)
    else:
        matches = np.concatenate(matches, axis=0)

    return matches, np.array(unmatched_detections), np.array(unmatched_trackers)


class Sort:
    """
    SORT: Simple Online and Realtime Tracking.
    
    Parameters:
        max_age: Maximum frames to keep alive a track without detection
        min_hits: Minimum hits before track is reported
        iou_threshold: Minimum IoU for matching
    """

    def __init__(self, max_age: int = 5, min_hits: int = 3, iou_threshold: float = 0.3):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.trackers: list[KalmanBoxTracker] = []
        self.frame_count = 0

    def update(self, detections: np.ndarray = np.empty((0, 5))) -> np.ndarray:
        """
        Update tracker with detected bounding boxes.
        
        Args:
            detections: Array of shape (N, 5) with [x1, y1, x2, y2, confidence]
        
        Returns:
            Array of shape (M, 5) with [x1, y1, x2, y2, track_id]
        """
        self.frame_count += 1

        # Predict new locations of existing trackers
        trks = np.zeros((len(self.trackers), 5))
        to_del = []
        for t, trk in enumerate(trks):
            pos = self.trackers[t].predict()[0]
            trk[:] = [pos[0], pos[1], pos[2], pos[3], 0]
            if np.any(np.isnan(pos)):
                to_del.append(t)

        trks = np.ma.compress_rows(np.ma.masked_invalid(trks))
        for t in reversed(to_del):
            self.trackers.pop(t)

        # Associate detections to trackers
        matched, unmatched_dets, unmatched_trks = associate_detections_to_trackers(
            detections[:, :4] if len(detections) > 0 else np.empty((0, 4)),
            trks[:, :4] if len(trks) > 0 else np.empty((0, 4)),
            self.iou_threshold,
        )

        # Update matched trackers
        for m in matched:
            self.trackers[m[1]].update(detections[m[0], :4])

        # Create new trackers for unmatched detections
        for i in unmatched_dets:
            trk = KalmanBoxTracker(detections[i, :4])
            self.trackers.append(trk)

        # Build output
        ret = []
        i = len(self.trackers)
        for trk in reversed(self.trackers):
            d = trk.get_state()[0]
            if (trk.time_since_update < 1) and (
                trk.hit_streak >= self.min_hits or self.frame_count <= self.min_hits
            ):
                ret.append(np.concatenate((d, [trk.id + 1])).reshape(1, -1))
            i -= 1
            # Remove dead tracks
            if trk.time_since_update > self.max_age:
                self.trackers.pop(i)

        if len(ret) > 0:
            return np.concatenate(ret)
        return np.empty((0, 5))

    def get_tracker_by_id(self, track_id: int) -> KalmanBoxTracker:
        """Get a tracker by its ID."""
        for trk in self.trackers:
            if trk.id + 1 == track_id:
                return trk
        return None
