import React, { useMemo, useState, useEffect } from 'react'
import { get_request } from '../request'
import { useNavigate } from 'react-router-dom';

let cache = {
    problems: [],
    totalPages: 1,
    page: 1,
    filter: { code: '', name: '', authors: '' },
	loading: true
};

export default function ProblemList() {
    const [problems, setProblems] = useState(cache.problems)
    const [totalPages, setTotalPages] = useState(cache.totalPages)
    const [page, setPage] = useState(cache.page)
    const [filter, setFilter] = useState(cache.filter)
    const [loading, setLoading] = useState(cache.loading)

    const navigate = useNavigate();

    const onFilterChange = (e) => {
        const { name, value } = e.target
        const newFilter = { ...filter, [name]: value }
        setFilter(newFilter)
        setPage(1)
        // Cập nhật vào cache
        cache.filter = newFilter
        cache.page = 1
    }

    const handlePageChange = (p) => {
        setPage(p)
        cache.page = p
    }

    useEffect(() => {
        let mounted = true;

        const fetchProblems = async () => {
            const params = new URLSearchParams({ page: page })
            if (filter.code) params.append("code", filter.code)
            if (filter.name) params.append("name", filter.name)
            if (filter.authors) params.append("authors", filter.authors)

            try {
                const res = await get_request(`/api/problem?${params.toString()}`)
                if (!mounted) return

                if (res && res.data) {
                    const data = res.data.problems || []
                    const total = res.data.total_pages || 1
                    
                    setProblems(data)
                    setTotalPages(total)

                    cache.problems = data
                    cache.totalPages = total
                }
            } catch (err) {
                console.error("Failed to load", err)
            } finally {
                if (mounted){
					setLoading(false)
					cache.loading = false
				}
            }
        }
        const timeoutId = setTimeout(fetchProblems, 300)
        return () => { mounted = false; clearTimeout(timeoutId) }
    }, [page, filter])

    // Logic thanh phân trang
    const pagesToShow = useMemo(() => {
        const startCount = 2, endCount = 2, middleCount = 6
        const total = totalPages

        if (total <= startCount + middleCount + endCount) {
            return Array.from({ length: total }, (_, i) => i + 1)
        }

        const pagesSet = new Set()
        for (let i = 1; i <= Math.min(startCount, total); i++) pagesSet.add(i)

        const half = Math.floor(middleCount / 2)
        let middleStart = page - half
        let middleEnd = middleStart + middleCount - 1

        if (middleStart <= startCount) {
            middleStart = startCount + 1
            middleEnd = middleStart + middleCount - 1
        }
        if (middleEnd >= total - endCount + 1) {
            middleEnd = total - endCount
            middleStart = middleEnd - middleCount + 1
        }
        for (let i = middleStart; i <= middleEnd; i++) pagesSet.add(i)
        for (let i = Math.max(total - endCount + 1, startCount + 1); i <= total; i++) pagesSet.add(i)

        return Array.from(pagesSet).sort((a, b) => a - b)
    }, [totalPages, page])

    return (
        <>
            <h1 className="title">Problems</h1>
            <div className="box">
                {/* Thanh phân trang */}
                <nav className="pagination is-centered" role="navigation" aria-label="pagination">
                    <button className="pagination-previous"
                        onClick={(e) => { e.preventDefault(); setPage((p) => Math.max(1, p - 1)) }}
                        disabled={page === 1}
                    >Previous</button>
                    <button className="pagination-next"
                        onClick={(e) => { e.preventDefault(); setPage((p) => Math.min(totalPages, p + 1)) }}
                        disabled={page === totalPages}
                    >Next</button>

                    <ul className="pagination-list">
                        {pagesToShow.map((p, i) => {
                            const prev = pagesToShow[i - 1]
                            return (
                                <React.Fragment key={p}>
                                    {prev && p - prev > 1 && <li><span className="pagination-ellipsis">&hellip;</span></li>}
                                    <li>
                                        <button className={`pagination-link ${page === p ? 'is-current' : ''}`} onClick={() => setPage(p)}>
                                            {p}
                                        </button>
                                    </li>
                                </React.Fragment>
                            )
                        })}
                    </ul>
                </nav>

                <table className="table is-hoverable is-fullwidth" width="100%">
                    <thead>
                        {/* 3 Cột tiêu đề */}
                        <tr>
                            <th width="20%">Code</th>
                            <th>Name</th>
                            <th width="30%">Authors</th>
                        </tr>
                        {/* 3 Ô input filter */}
                        <tr>
                            <th>
                                <input className="input" type="text" placeholder="Filter Code" name="code" value={filter.code} onChange={onFilterChange} />
                            </th>
                            <th>
                                <input className="input" type="text" placeholder="Filter Name" name="name" value={filter.name} onChange={onFilterChange} />
                            </th>
                            <th>
                                <input className="input" type="text" placeholder="Filter Authors" name="authors" value={filter.authors} onChange={onFilterChange} />
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr>
                                <td colSpan={3} style={{ textAlign: 'center' }}>Loading problems…</td>
                            </tr>
                        ) : problems.length === 0 ? (
                            <tr>
                                <td colSpan={3} style={{ textAlign: 'center' }}>No problems match your filters</td>
                            </tr>
                        ) : (
                            problems.map((p) => (
                                <tr key={p.code} style={{cursor: 'pointer'}} onClick={() => navigate(`/p/${p.code}`)}>
                                    <td>{p.code}</td>
                                    <td>{p.name}</td>
                                    <td>
										{p.authors && p.authors.length > 0 && 
											p.authors.map(a => a.username || a.name).join(', ')
										}
									</td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </>
    )
}