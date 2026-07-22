import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { get_request } from '../Request';
import { Link, useParams, useSearchParams } from 'react-router-dom';

import { useAuth } from '../context/AuthContext';
import { HandleDisplay } from '../components/HandleDisplay';
import SubmitModal from '../components/problem/SubmitModal';
import SubmissionList from '../components/problem/SubmissionList';

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

const fetchProblem = async (id, contestCode) => {
  const query = contestCode ? `?contest=${encodeURIComponent(contestCode)}` : '';
  const res = await get_request(`/problem/${id}${query}`);
  return res.data;
};

export default function ProblemDisplay() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const contestCode = searchParams.get('contest');
  const {current_user, loginRequired} = useAuth();
  const [isSubmitModalOpen, setIsSubmitModalOpen] = useState(false);
  const [submissionList, setSubmissionList] = useState({ isOpen: false, mode: 'status' });
  const openSubmissionList = (mode) => setSubmissionList({ isOpen: true, mode });
  const closeSubmissionList = () => setSubmissionList(prev => ({ ...prev, isOpen: false }));

  // query state
  const { data: p = {}, isLoading, error } = useQuery({
    queryKey: ['problem', id, contestCode],
    queryFn: () => fetchProblem(id, contestCode),
    staleTime: 1000 * 60 * 5,
  });

  // loading / error handler
  if (isLoading || error) return (
    <>
      <h1 className="title">Bài {id}</h1>
      <div className="box">
        {isLoading ? "Loading…" : `Error: ${error.message || "Không thể tải đề bài"}`}
      </div>
    </>
  );

  return (
    <div className="columns">
      {/* Left column: Function buttons and problem infos */}
      <div className="column is-one-fifth">
        <div className='buttons is-centered'>
          <button onClick={() => loginRequired(() => setIsSubmitModalOpen(true))} className="button is-primary is-fullwidth">Submit</button>
          <button onClick={() => loginRequired(() => openSubmissionList('status'))} className="button is-info"><i className="fas fa-signal"/></button>
          <button onClick={() => loginRequired(() => openSubmissionList('my-submissions'))} className="button is-info"><i className="fas fa-user-circle"/></button>
          <button onClick={() => loginRequired(() => openSubmissionList('leaderboard'))} className="button is-link"><i className="fas fa-crown"/></button>
          <button className="button is-link"><i className="fas fa-edit"/></button>
        </div>
        
        <div className='box'>
          <p><strong>Time limit:</strong> {p.time_limit} ms</p>
          <p><strong>Memory limit:</strong> {p.memory_limit ? p.memory_limit / 1024 : 0} MB</p>
          <p><strong>Input:</strong> {p.input || 'stdin'}</p>
          <p><strong>Output:</strong> {p.output || 'stdout'}</p>
          {p.authors?.length > 0 && (
            <p><strong>Tác giả:</strong> {p.authors.map(a => HandleDisplay(a)).join(', ')}</p>
          )}
        </div>
      </div>
      
      {/* Right column: Problem title and statement (Markdown+LaTeX is not working lmao) */}
      <div className="column">
        <h1 className="title">{p.name || `Bài ${id}`} <span className="has-text-grey-light">({p.code})</span></h1>
        {contestCode && <p className="subtitle is-6">Contest: <Link to={`/contest/${contestCode}`}>{contestCode}</Link></p>}
        <hr />
        <ReactMarkdown
          remarkPlugins={[remarkGfm, remarkMath]}
          rehypePlugins={[rehypeKatex]}
        >
          {p.statement || ""}
        </ReactMarkdown>
      </div>

      {/* Modals */}
      <SubmitModal 
        isOpen={isSubmitModalOpen}
        onClose={() => setIsSubmitModalOpen(false)}
        problemId={id}
        problemName={p.name}
        contestCode={contestCode}
      />
      <SubmissionList 
        isOpen={submissionList.isOpen}
        onClose={closeSubmissionList}
        problemId={id}
        mode={submissionList.mode}
        username={current_user?.username || ""}
        contestCode={contestCode}
      />
    </div>
  );
}