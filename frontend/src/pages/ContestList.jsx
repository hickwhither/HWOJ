import React, { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { get_request } from '../Request';

const fetchContests = async ({ page, filter }) => {
  const params = new URLSearchParams({ page });
  if (filter.code) params.append('code', filter.code);
  if (filter.name) params.append('name', filter.name); // Changed from 'title' to 'name'
  
  const res = await get_request(`/contest?${params.toString()}`);
  // Fallback structure adjusted to match the new JSON response
  return res?.data || { items: [], pages: 1 }; 
};

const formatDate = (value) => value ? new Date(value).toLocaleString() : '-';

export default function ContestList() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [filter, setFilter] = useState({ code: '', name: '' }); // Changed 'title' to 'name'

  const { data, isLoading, isPlaceholderData } = useQuery({
    queryKey: ['contests', { page, filter }],
    queryFn: () => fetchContests({ page, filter }),
    staleTime: 1000 * 60 * 5,
    placeholderData: (prev) => prev,
  });

  // Extract from the new JSON keys
  const contests = data?.items || []; 
  const totalPages = data?.pages || 1;

  const pagesToShow = useMemo(() => {
    const total = Math.max(1, totalPages);
    return Array.from({ length: total }, (_, i) => i + 1);
  }, [totalPages]);

  const onFilterChange = (e) => {
    const { name, value } = e.target;
    setFilter(prev => ({ ...prev, [name]: value }));
    setPage(1);
  };

  return (
    <>
      <h1 className="title">Contests</h1>
      <div className="box">
        <nav className="pagination is-centered" role="navigation" aria-label="pagination">
          <button className="pagination-previous" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>Previous</button>
          <button className="pagination-next" onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>Next</button>
          <ul className="pagination-list">
            {pagesToShow.map((p) => (
              <li key={p}>
                <button className={`pagination-link ${page === p ? 'is-current' : ''}`} onClick={() => setPage(p)}>{p}</button>
              </li>
            ))}
          </ul>
        </nav>

        <table className="table is-hoverable is-fullwidth">
          <thead>
            <tr>
              <th width="20%">Code</th>
              <th>Name</th> {/* Changed Title to Name */}
              <th width="20%">Start</th>
              <th width="20%">End</th>
            </tr>
            <tr>
              <th><input className="input" type="text" placeholder="Filter Code" name="code" value={filter.code} onChange={onFilterChange} /></th>
              <th><input className="input" type="text" placeholder="Filter Name" name="name" value={filter.name} onChange={onFilterChange} /></th>
              <th />
              <th />
            </tr>
          </thead>
          <tbody style={{ opacity: isPlaceholderData ? 0.6 : 1 }}>
            {isLoading ? (
              <tr><td colSpan={4} className="has-text-centered">Loading contests…</td></tr>
            ) : contests.length === 0 ? (
              <tr><td colSpan={4} className="has-text-centered">No contests match your filters</td></tr>
            ) : contests.map((contest) => (
              <tr key={contest.code} style={{ cursor: 'pointer' }} onClick={() => navigate(`/c/${contest.code}`)}>
                <td>{contest.code}</td>
                <td>{contest.name}</td> {/* Using contest.name instead of contest.title */}
                <td>{formatDate(contest.start_time)}</td>
                <td>{formatDate(contest.end_time)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}