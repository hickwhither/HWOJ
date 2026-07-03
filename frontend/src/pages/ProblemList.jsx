import React, { useMemo, useState, useEffect } from 'react'
import { get_request } from '../request'
import { useNavigate } from 'react-router-dom';

const STORAGE_KEY = "problems_cache"
const COOLDOWN = 60_000 // 60 seconds

export default function ProblemList() {
	const [ojs, setOjs] = useState(new Set())
	const [problems, setProblems] = useState(() => {
		const cache = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}")
		return cache.data || []
	})
	const [loadingProblem, setLoadingProblem] = useState(true)

	useEffect(() => {
		let mounted = true

		async function load() {
			const now = Date.now()
			const cache = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}")
			const lastFetch = cache.lastFetch || 0

			if (now - lastFetch < COOLDOWN && cache.data) {
				if (mounted) {
					setProblems(cache.data)
					setOjs(new Set(cache.data.map(p => p.oj)))
					setLoadingProblem(false)
				}
				return
			}

			try {
				const res = await get_request("/api/problems")
				if (!mounted) return

				if (res && res.json) {
					const newCache = {
						data: res.json,
						lastFetch: now
					}

					localStorage.setItem(STORAGE_KEY, JSON.stringify(newCache))
					setProblems(res.json)
					setOjs(new Set(res.json.map(p => p.oj)))
				}
			} catch (err) {
				console.error("Failed to load /api/problems", err)
			} finally {
				if (mounted) setLoadingProblem(false)
			}
		}

		load()
		return () => { mounted = false }
	}, [])
	
	const [page, setPage] = useState(1);
	const [filter, setFilter] = useState({
		oj: "all",
		page: 1,
		problemid: '',
		title: '',
		min_rating: '',
		max_rating: ''
	})

	const onFilterChange = (e) => {
		const { name, value } = e.target
		setFilter((prev) => ({ ...prev, [name]: value }))
		setPage(1)
	}

	const filteredProblems = useMemo(() => {
		return problems.filter((p) => {
			if (filter.oj !== 'all' && p.oj !== filter.oj) return false
			if (filter.problemid && !String(p.id || p.prob).toLowerCase().includes(filter.problemid.toLowerCase())) return false
			if (filter.title && !String(p.title).toLowerCase().includes(filter.title.toLowerCase())) return false
			const min = filter.min_rating ? Number(filter.min_rating) : Number.NEGATIVE_INFINITY
			const max = filter.max_rating ? Number(filter.max_rating) : Number.POSITIVE_INFINITY
			if (p.rating < min || p.rating > max) return false
			return true
		})
	}, [problems, filter])

	const totalPages = Math.max(1, Math.ceil(filteredProblems.length / 20))
	const safePage = Math.min(Math.max(1, page), totalPages)
	const currentProblems = filteredProblems.slice((safePage - 1) * 20, safePage * 20)

	const pagesToShow = useMemo(() => {
		const startCount = 2
		const endCount = 2
		const middleCount = 6
		const total = totalPages

		// If total is small, show all pages
		if (total <= startCount + middleCount + endCount) {
			return Array.from({ length: total }, (_, i) => i + 1)
		}

		const pagesSet = new Set()
		// Start pages
		for (let i = 1; i <= Math.min(startCount, total); i++) pagesSet.add(i)

		// Middle pages calculation
		const half = Math.floor(middleCount / 2)
		let middleStart = safePage - half
		let middleEnd = middleStart + middleCount - 1

		// Ensure the middle range is in bounds and doesn't collide with start/end
		if (middleStart <= startCount) {
			middleStart = startCount + 1
			middleEnd = middleStart + middleCount - 1
		}
		if (middleEnd >= total - endCount + 1) {
			middleEnd = total - endCount
			middleStart = middleEnd - middleCount + 1
		}
		for (let i = middleStart; i <= middleEnd; i++) pagesSet.add(i)

		// End pages
		for (let i = Math.max(total - endCount + 1, startCount + 1); i <= total; i++) pagesSet.add(i)

		return Array.from(pagesSet).sort((a, b) => a - b)
	}, [totalPages, safePage, filteredProblems.length])

	const navigate = useNavigate()

	return (
		<>
			<h1 className="title">Problems</h1>
			<div className="box">
				<nav className="pagination is-centered" role="navigation" aria-label="pagination">
					<button className="pagination-previous"
						onClick={(e) => { e.preventDefault(); setPage((p) => Math.max(1, p - 1)) }}
						disabled={safePage === 1}
					>Previous</button>
					<button className="pagination-next"
						onClick={(e) => { e.preventDefault(); setPage((p) => Math.min(totalPages, p + 1)) }}
						disabled={safePage === totalPages}
					>Next</button>

					<ul className="pagination-list">
						{pagesToShow.map((p, i) => {
							const prev = pagesToShow[i - 1]
							return (
								<React.Fragment key={p}>
									{prev && p - prev > 1 && (
										<li>
											<span className="pagination-ellipsis">&hellip;</span>
										</li>
									)}

									<li>
										<button
											className={`pagination-link ${safePage === p ? 'is-current' : ''}`}
											aria-label={`Goto page ${p}`}
											aria-current={safePage === p ? 'page' : undefined}
											onClick={() => setPage(p)}
										>
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
						<tr>
							<th width="5%">OJ</th>
							<th width="25%">Prob</th>
							<th>Title</th>
							<th width="15%">Rating</th>
							<th width="20%">Last update</th>
						</tr>
						<tr>
							<th>
								<div className="select" style={{ width: '100%' }}>
									<select name="oj"
										value={filter.oj}
										onChange={onFilterChange}
									>
									<option value="all">All</option>
									{[...ojs].map((oj, i) =>
										<option key={i} value={oj}>{oj}</option>
									)}
									</select>
								</div>
							</th>
							<th>
								<input className="input" type="text" placeholder="Prob" name="problemid" value={filter.problemid} onChange={onFilterChange} />
							</th>
							<th>
								<input className="input" type="text" placeholder="Title"
									name="title"
									value={filter.title}
									onChange={onFilterChange}
								/>
							</th>
							<th>
								<div className="block columns">
									<input className="input column" type="number" placeholder="Min"
										name="min_rating"
										value={filter.min_rating}
										onChange={onFilterChange}
									/>
									<input className="input column" type="number" placeholder="Max"
										name="max_rating"
										value={filter.max_rating}
										onChange={onFilterChange}
									/>
								</div>
							</th>
							<th>Last update</th>
						</tr>
					</thead>
					<tbody id="problem-list">
						{(problems == []) ? (
							<tr>
								<td colSpan={5} style={{ textAlign: 'center' }}>Loading problems…</td>
							</tr>
						) : currentProblems.length === 0 ? (
							<tr>
								<td colSpan={5} style={{ textAlign: 'center' }}>No problems match your filters</td>
							</tr>
						) : (
							currentProblems.map((p) => (
								<tr key={p.id || p.prob} onClick={() => navigate(`/p/${p.id}`)}>
									<td>{p.oj}</td>
									<td>{p.id}</td>
									<td>{p.title}</td>
									<td>{p.rating}</td>
									<td>{p.updated_at || p.updated}</td>
								</tr>
							))
						)}
					</tbody>
				</table>

			</div>
		</>
	)
}
