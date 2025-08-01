import React, { useState, useEffect } from 'react';
import './ApprovalComponent.css';

const ApprovalComponent = ({ projectId, onApprovalUpdate }) => {
    const [pendingApprovals, setPendingApprovals] = useState([]);
    const [selectedApproval, setSelectedApproval] = useState(null);
    const [approvalStats, setApprovalStats] = useState(null);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');

    useEffect(() => {
        if (projectId) {
            fetchPendingApprovals();
            fetchApprovalStats();
        }
    }, [projectId]);

    const fetchPendingApprovals = async () => {
        try {
            setLoading(true);
            const response = await fetch(`/approval/pending/${projectId}`);
            const data = await response.json();
            
            if (data.success) {
                setPendingApprovals(data.pending_approvals);
            } else {
                setMessage(`Error: ${data.error}`);
            }
        } catch (error) {
            setMessage(`Error fetching approvals: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const fetchApprovalStats = async () => {
        try {
            const response = await fetch(`/approval/stats/${projectId}`);
            const data = await response.json();
            
            if (data.success) {
                setApprovalStats(data.statistics);
            }
        } catch (error) {
            console.error('Error fetching approval stats:', error);
        }
    };

    const handleApprovalAction = async (approvalId, action, notes = '') => {
        try {
            setLoading(true);
            const response = await fetch(`/approval/${approvalId}/${action}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: 'current_user', // In real app, get from auth
                    notes: notes,
                    reason: action === 'deny' ? notes : ''
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                setMessage(`Content ${action === 'approve' ? 'approved' : 'denied'} successfully`);
                fetchPendingApprovals();
                fetchApprovalStats();
                if (onApprovalUpdate) {
                    onApprovalUpdate();
                }
            } else {
                setMessage(`Error: ${data.error}`);
            }
        } catch (error) {
            setMessage(`Error: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const handleViewDetails = async (approvalId) => {
        try {
            const response = await fetch(`/approval/${approvalId}`);
            const data = await response.json();
            
            if (data.success) {
                setSelectedApproval(data.approval);
            } else {
                setMessage(`Error: ${data.error}`);
            }
        } catch (error) {
            setMessage(`Error: ${error.message}`);
        }
    };

    const formatTime = (timestamp) => {
        return new Date(timestamp).toLocaleString();
    };

    const getSensitivityFlagColor = (flag) => {
        const flagColors = {
            'Potential PII detected': '#ff6b6b',
            'Multiple cultural references detected': '#4ecdc4',
            'Potential financial/confidential data detected': '#45b7d1'
        };
        return flagColors[flag] || '#95a5a6';
    };

    return (
        <div className="approval-component">
            <div className="approval-header">
                <h2>Content Approval Workflow</h2>
                {approvalStats && (
                    <div className="approval-stats">
                        <div className="stat-item">
                            <span className="stat-label">Total Requests:</span>
                            <span className="stat-value">{approvalStats.total_requests}</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-label">Pending:</span>
                            <span className="stat-value pending">{approvalStats.pending}</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-label">Approved:</span>
                            <span className="stat-value approved">{approvalStats.approved}</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-label">Denied:</span>
                            <span className="stat-value denied">{approvalStats.denied}</span>
                        </div>
                    </div>
                )}
            </div>

            {message && (
                <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
                    {message}
                </div>
            )}

            {loading && (
                <div className="loading">
                    <div className="spinner"></div>
                    Processing...
                </div>
            )}

            <div className="approval-content">
                <div className="pending-approvals">
                    <h3>Pending Approvals ({pendingApprovals.length})</h3>
                    
                    {pendingApprovals.length === 0 ? (
                        <div className="no-approvals">
                            <p>No pending approvals for this project.</p>
                        </div>
                    ) : (
                        <div className="approval-list">
                            {pendingApprovals.map((approval) => (
                                <div key={approval.approval_id} className="approval-item">
                                    <div className="approval-header">
                                        <h4>Approval ID: {approval.approval_id}</h4>
                                        <span className="approval-date">
                                            {formatTime(approval.created_at)}
                                        </span>
                                    </div>
                                    
                                    <div className="approval-content-preview">
                                        <p className="content-preview">
                                            {approval.response_text.substring(0, 200)}...
                                        </p>
                                    </div>
                                    
                                    <div className="sensitivity-flags">
                                        <h5>Sensitivity Flags:</h5>
                                        {approval.sensitivity_flags.map((flag, index) => (
                                            <span 
                                                key={index} 
                                                className="sensitivity-flag"
                                                style={{ backgroundColor: getSensitivityFlagColor(flag) }}
                                            >
                                                {flag}
                                            </span>
                                        ))}
                                    </div>
                                    
                                    <div className="approval-actions">
                                        <button 
                                            className="btn-view"
                                            onClick={() => handleViewDetails(approval.approval_id)}
                                        >
                                            View Details
                                        </button>
                                        <button 
                                            className="btn-approve"
                                            onClick={() => handleApprovalAction(approval.approval_id, 'approve')}
                                            disabled={loading}
                                        >
                                            Approve
                                        </button>
                                        <button 
                                            className="btn-deny"
                                            onClick={() => handleApprovalAction(approval.approval_id, 'deny')}
                                            disabled={loading}
                                        >
                                            Deny
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {selectedApproval && (
                    <div className="approval-details-modal">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h3>Approval Details</h3>
                                <button 
                                    className="close-btn"
                                    onClick={() => setSelectedApproval(null)}
                                >
                                    ×
                                </button>
                            </div>
                            
                            <div className="modal-body">
                                <div className="detail-section">
                                    <h4>Response Content</h4>
                                    <div className="response-content">
                                        {selectedApproval.response_text}
                                    </div>
                                </div>
                                
                                <div className="detail-section">
                                    <h4>Evaluation Results</h4>
                                    <div className="evaluation-results">
                                        <p><strong>Cultural Score:</strong> {selectedApproval.evaluation_result?.cultural_score || 'N/A'}</p>
                                        <p><strong>Recommendations:</strong></p>
                                        <ul>
                                            {selectedApproval.evaluation_result?.recommendations?.map((rec, index) => (
                                                <li key={index}>{rec}</li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                                
                                <div className="detail-section">
                                    <h4>Sensitivity Analysis</h4>
                                    <div className="sensitivity-analysis">
                                        {selectedApproval.sensitivity_flags.map((flag, index) => (
                                            <span 
                                                key={index} 
                                                className="sensitivity-flag"
                                                style={{ backgroundColor: getSensitivityFlagColor(flag) }}
                                            >
                                                {flag}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                                
                                <div className="detail-section">
                                    <h4>Approval Actions</h4>
                                    <div className="approval-actions-detailed">
                                        <button 
                                            className="btn-approve"
                                            onClick={() => {
                                                handleApprovalAction(selectedApproval.approval_id, 'approve');
                                                setSelectedApproval(null);
                                            }}
                                            disabled={loading}
                                        >
                                            Approve Content
                                        </button>
                                        <button 
                                            className="btn-deny"
                                            onClick={() => {
                                                handleApprovalAction(selectedApproval.approval_id, 'deny');
                                                setSelectedApproval(null);
                                            }}
                                            disabled={loading}
                                        >
                                            Deny Content
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ApprovalComponent; 