import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { get_request } from '../../Request';

const fetchSubmissions = async ({ problemId, mode, username }) => {
  if (mode === 'leaderboard') {
    const res = await get_request(`/submission/rank/${problemId}`);
    return res?.data || res || [];
  }
  const baseUrl = `/submission/problem/${problemId}`;
  const url = mode === 'my-submissions' && username 
    ? `${baseUrl}?username=${encodeURIComponent(username)}` 
    : baseUrl;

  const res = await get_request(url);
  return res?.data || res || [];
};

export default function SubmissionList({ isOpen, onClose, problemId, mode, username }) {
  const { data: list = [], isLoading } = useQuery({
    queryKey: ['submissions', { problemId, mode, username }],
    queryFn: () => fetchSubmissions({ problemId, mode, username }),
    staleTime: 1000 * 10,
    enabled: isOpen
  });

  const isRank = mode === 'leaderboard';
  const isMySubmissions = mode === 'my-submissions';

  // Định nghĩa tiêu đề tương ứng với từng chế độ
  const getTitle = () => {
    if (isRank) return '🏆 Leaderboard';
    if (isMySubmissions) return '👤 Bài nộp của tôi';
    return '📜 Tất cả bài nộp';
  };

  return (
    <div className={`modal ${isOpen ? "is-active" : ""}`}>
      <div className="modal-background" onClick={onClose}></div>
      <div className="modal-content" style={{ width: '80%', maxWidth: '900px' }}>
        <div className="box">
          <h2 className="title is-4">{getTitle()}</h2>

          {isLoading ? (
            <div className="has-text-centered py-5">Loading dữ liệu...</div>
          ) : list.length === 0 ? (
            <div className="has-text-centered has-text-grey py-5">Chưa có bài nộp nào.</div>
          ) : (
            <div className="table-container">
              <table className="table is-fullwidth is-striped is-hoverable">
                <thead>
                  <tr>
                    {isRank && <th width="8%">Hạng</th>}
                    <th>ID</th>
                    <th>Người nộp</th>
                    <th>Ngôn ngữ</th>
                    <th>Kết quả</th>
                    <th>Thời gian</th>
                    <th>Bộ nhớ</th>
                  </tr>
                </thead>
                <tbody>
                  {list.map((sub, index) => (
                    <tr key={sub.id}>
                      {isRank && <td><strong>{index + 1}</strong></td>}
                      <td>#{sub.id}</td>
                      <td>{sub.user?.username}</td>
                      <td><span className="tag is-light">{sub.language}</span></td>
                      <td>
                        <span className={`tag is-bold`}>
                          {sub.percentage}% ({sub.status})
                        </span>
                      </td>
                      <td>{sub.time_used} ms</td>
                      <td>{(sub.memory_used / 1024).toFixed(2)} MB</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
      <button className="modal-close is-large" aria-label="close" onClick={onClose}></button>
    </div>
  );
}