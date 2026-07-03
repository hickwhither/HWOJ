import React, { useMemo, useState, useEffect } from 'react'
import { get_request } from '../request'
import { useNavigate, useParams } from 'react-router-dom';

const STORAGE_KEY = "problems_cache"
const COOLDOWN = 60_000 // 60 seconds

export default function ProblemDisplay() {
	const { id } = useParams();
	const navigate = useNavigate();
	const [problem, setProblem] = useState(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState(null);

	useEffect(() => {
		let mounted = true;
		async function load() {
			setLoading(true);
			try {
				const res = await get_request(`/api/problem/${id}`);
				if (!mounted) return;
				setProblem(res && res.json ? res.json : null);
			} catch (e) {
				setError(e.message || String(e));
			} finally {
				if (mounted) setLoading(false);
			}
		}
		load();
		return () => { mounted = false };
	}, [id]);

	if (loading) return (
		<>
			<h1 className="title">Bai {id}</h1>
			<div className="box">Loading…</div>
		</>
	);

	if (error) return (
		<>
			<h1 className="title">Bai {id}</h1>
			<div className="box">Error: {error}</div>
		</>
	);

	const p = problem || {};
	const rating = p.rating == null ? '—' : p.rating;

	return (
		<>
			<h1 className="title">{p.title || `Bai ${id}`}</h1>
			<div className="box">
				<p><strong>OJ:</strong> {p.oj}</p>
				<p><strong>ID:</strong> {p.id}</p>
				<p><strong>Rating:</strong> {rating}</p>
				<p><strong>Last update:</strong> {p.updated_at || p.updated}</p>
				<div dangerouslySetInnerHTML={{ __html: p.description || p.translated || 'No description' }} />
			</div>
		</>
	)
}
