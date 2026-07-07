import React, { useState, useEffect } from 'react';
import { get_request } from '../request';
import { useNavigate, useParams } from 'react-router-dom';

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

const problemCache = {};

export default function ProblemDisplay() {
    const { id } = useParams();
    const [problem, setProblem] = useState(problemCache[id] || null); // 2. Khởi tạo từ cache
    const [loading, setLoading] = useState(!problemCache[id]); // 3. Nếu có cache thì không loading
    const [error, setError] = useState(null);

    useEffect(() => {
        if (problemCache[id]) {
            setProblem(problemCache[id]);
            setLoading(false);
            return;
        }

        let mounted = true;
        async function load() {
            setLoading(true);
            setError(null);
            try {
                const res = await get_request(`/api/problem/${id}`);
                if (!mounted) return;
                
                const data = res && res.data ? res.data : res; 
                
                // 4. Lưu vào cache trước khi set state
                problemCache[id] = data;
                setProblem(data);
            } catch (e) {
                if (!mounted) return;
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
            <h1 className="title">Bài {id}</h1>
            <div className="box">Loading…</div>
        </>
    );

    if (error) return (
        <>
            <h1 className="title">Bài {id}</h1>
            <div className="box">Error: {error}</div>
        </>
    );

    const p = problem || {};

    return (
        <>
            <h1 className="title">{p.name || `Bài ${id}`} <span className="has-text-grey-light">({p.code})</span></h1>
            
            <div className="box">
                <p><strong>Time limit:</strong> {p.time_limit} ms</p>
                <p><strong>Memory limit:</strong> {p.memory_limit/1024} MB</p>
                <p><strong>Input:</strong> {p.input ? p.input : 'stdin'}</p>
                <p><strong>Output:</strong> {p.output ? p.output : 'stdout'}</p>
				{/* Cần thay gấp bằng 1 cái load username */}
                {p.authors && p.authors.length > 0 && (
                    <p><strong>Tác giả:</strong> {p.authors.map(a => a.username || a.name).join(', ')}</p>
                )}

                <hr />
                <ReactMarkdown
                    remarkPlugins={[remarkGfm, remarkMath]}
                    rehypePlugins={[rehypeKatex]}
                >
                    {p.statement}
                </ReactMarkdown>
            </div>
        </>
    )
}