import React, { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { get_request } from '../Request';
import { useNavigate } from 'react-router-dom';

const fetchProblems = async ({ page, filter }) => {
  const params = new URLSearchParams({ page });
  if (filter.code) params.append("code", filter.code);
  if (filter.name) params.append("name", filter.name);
  if (filter.authors) params.append("authors", filter.authors);
  
  const res = await get_request(`/problems?${params.toString()}`);
  return res?.data || { items: [], pages: 1, total: 0, page: 1, size: 10 };
};

export default function ProblemList() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [filter, setFilter] = useState({ code: '', name: '', authors: '' });

  // Query state từ React Query
  const { data, isLoading, isPlaceholderData } = useQuery({
    queryKey: ['problems', { page, filter }],
    queryFn: () => fetchProblems({ page, filter }),
    staleTime: 1000 * 60 * 5,
    placeholderData: (prev) => prev,
  });
  
  // Trích xuất danh sách bài tập (items) và tổng số trang (pages) từ JSON API mới
  const problems = data?.items || [];
  const totalPages = data?.pages || 1;

  const onFilterChange = (e) => {
    const { name, value } = e.target;
    setFilter(prev => ({ ...prev, [name]: value }));
    setPage(1); // Reset về trang 1 khi lọc
  };

  // Tính toán các nút phân trang hiển thị
  const pagesToShow = useMemo(() => {
    const startCount = 2, endCount = 2, middleCount = 6;
    if (totalPages <= startCount + middleCount + endCount) {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }

    const pagesSet = new Set();
    for (let i = 1; i <= Math.min(startCount, totalPages); i++) pagesSet.add(i);

    const half = Math.floor(middleCount / 2);
    let start = page - half;
    let end = start + middleCount - 1;

    if (start <= startCount) {
      start = startCount + 1;
      end = start + middleCount - 1;
    }
    if (end >= totalPages - endCount + 1) {
      end = totalPages - endCount;
      start = end - middleCount + 1;
    }
    
    for (let i = start; i <= end; i++) pagesSet.add(i);
    for (let i = Math.max(totalPages - endCount + 1, startCount + 1); i <= totalPages; i++) pagesSet.add(i);

    return Array.from(pagesSet).sort((a, b) => a - b);
  }, [totalPages, page]);

  return (
    <>
      <h1 className="title">Problems</h1>
      <div className="box">
        
        {/* Pagination */}
        <nav className="pagination is-centered" role="navigation" aria-label="pagination">
          <button 
            className="pagination-previous"
            onClick={(e) => { e.preventDefault(); setPage(p => Math.max(1, p - 1)); }}
            disabled={page <= 1}
          >
            Previous
          </button>
          <button 
            className="pagination-next"
            onClick={(e) => { e.preventDefault(); setPage(p => Math.min(totalPages, p + 1)); }}
            disabled={page >= totalPages}
          >
            Next
          </button>

          <ul className="pagination-list">
            {pagesToShow.map((p, i) => {
              const prev = pagesToShow[i - 1];
              return (
                <React.Fragment key={p}>
                  {prev && p - prev > 1 && <li><span className="pagination-ellipsis">&hellip;</span></li>}
                  <li>
                    <button 
                      className={`pagination-link ${page === p ? 'is-current' : ''}`} 
                      onClick={() => setPage(p)}
                    >
                      {p}
                    </button>
                  </li>
                </React.Fragment>
              );
            })}
          </ul>
        </nav>

        {/* Problems Table */}
        <table className="table is-hoverable is-fullwidth" width="100%">
          <thead>
            <tr>
              <th width="20%">Code</th>
              <th>Name</th>
              <th width="30%">Authors</th>
            </tr>
            <tr>
              <th><input className="input" type="text" placeholder="Filter Code" name="code" value={filter.code} onChange={onFilterChange} /></th>
              <th><input className="input" type="text" placeholder="Filter Name" name="name" value={filter.name} onChange={onFilterChange} /></th>
              <th><input className="input" type="text" placeholder="Filter Authors" name="authors" value={filter.authors} onChange={onFilterChange} /></th>
            </tr>
          </thead>
          
          <tbody style={{ opacity: isPlaceholderData ? 0.6 : 1 }}> 
            {isLoading ? (
              <tr><td colSpan={3} style={{ textAlign: 'center' }}>Loading problems…</td></tr>
            ) : problems.length === 0 ? (
              <tr><td colSpan={3} style={{ textAlign: 'center' }}>No problems match your filters</td></tr>
            ) : (
              problems.map((p) => (
                <tr key={p.code} style={{ cursor: 'pointer' }} onClick={() => navigate(`/p/${p.code}`)}>
                  <td>{p.code}</td>
                  <td>{p.name}</td>
                  <td>
                    {Array.isArray(p.authors) 
                      ? p.authors.map(a => (typeof a === 'string' ? a : a.username || a.name)).join(', ')
                      : (p.authors || '')}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

      </div>
    </>
  );
}