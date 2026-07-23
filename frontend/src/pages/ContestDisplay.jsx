import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { get_request, post_request } from '../Request';
import { toast } from 'react-toastify';

const fetchContest = async (code) => {
  const res = await get_request(`/contest/${code}`);
  if (res.status !== 200) throw new Error(res.data?.detail || 'Không thể tải contest');
  return res.data;
};

const formatDate = (value) => value ? new Date(value).toLocaleString() : '-';

export default function ContestDisplay() {
  const { code } = useParams();
  const [password, setPassword] = useState('');
  const [registering, setRegistering] = useState(false);

  const { data: contest, isLoading, error, refetch } = useQuery({
    queryKey: ['contest', code],
    queryFn: () => fetchContest(code),
    staleTime: 1000 * 60 * 5,
  });

  const register = async (e) => {
    e.preventDefault();
    setRegistering(true);
    const res = await post_request(`/contest/${code}/register`, { password });
    setRegistering(false);
    if (res.status === 200) {
      toast.success('Đăng ký contest thành công!');
      refetch();
    } else {
      toast.error(res.data?.detail || 'Không thể đăng ký contest');
    }
  };

  if (isLoading) return <div className="box">Loading contest…</div>;
  if (error) return <div className="box has-text-danger">{error.message}</div>;

  return (
    <div className="columns">
      <div className="column is-one-quarter">
        <div className="box">
          <h2 className="title is-5">{contest.title || contest.code}</h2>
          <p><strong>Code:</strong> {contest.code}</p>
          <p><strong>Start:</strong> {formatDate(contest.start_time)}</p>
          <p><strong>End:</strong> {formatDate(contest.end_time)}</p>
          <hr />
          <form onSubmit={register}>
            <label className="label">Contest password</label>
            <input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Bỏ trống nếu không có" disabled={registering} />
            <button className={`button is-primary is-fullwidth mt-3 ${registering ? 'is-loading' : ''}`} disabled={registering}>Register</button>
          </form>
        </div>
      </div>

      <div className="column">
        <h1 className="title">{contest.title || contest.code}</h1>
        <div className="content">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{contest.description || ''}</ReactMarkdown>
        </div>

        <h2 className="title is-4 mt-5">Problems</h2>
        <div className="box">
          {contest.problems?.length > 0 ? (
            <table className="table is-hoverable is-fullwidth">
              <tbody>
                {contest.problems.map((problem) => (
                  <tr key={problem.code}>
                    <td><Link to={`/p/${problem.code}?contest=${contest.code}`}>{problem.code}</Link></td>
                    <td>{problem.name}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="has-text-grey">Contest chưa có bài.</p>
          )}
        </div>
      </div>
    </div>
  );
}
