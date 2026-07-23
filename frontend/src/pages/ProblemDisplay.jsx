import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useParams, useSearchParams } from 'react-router-dom';
import { get_request } from '../Request';

import { useAuth } from '../context/AuthContext';
import { HandleDisplay } from '../components/HandleDisplay';
import SubmitModal from '../components/problem/SubmitModal';
import SubmissionList from '../components/problem/SubmissionList';

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

// IMPORTANT: Import CSS của KaTeX để công thức Toán hiển thị đúng! (AI noi vay chu tui hok biet)
import 'katex/dist/katex.min.css';

const fetchProblem = async (problem_code, contest_code) => {
  const params = new URLSearchParams({ problem_code });
  if (contest_code) params.contest_code = contest_code;

  // GET /problem?problem_code=...&contest_code=...
  const res = await get_request(`/problem?${params.toString()}`);
  return res.data;
};

export default function ProblemDisplay() {
  // p/:problem_code
  // p/:problem_code/:contest_code
  const { problem_code, contest_code: routeContestCode } = useParams();
  // /p/SUM?contest_code=CONTEST_01
  const [searchParams] = useSearchParams();
  const queryContestCode = searchParams.get('contest_code');

  // Ưu tiên contest_code từ Route param, nếu không có thì lấy từ Query string
  const contest_code = routeContestCode || queryContestCode || null;

  const { current_user, loginRequired } = useAuth();
  
  // Modals State
  const [isSubmitModalOpen, setIsSubmitModalOpen] = useState(false);
  const [submissionList, setSubmissionList] = useState({ isOpen: false, mode: 'status' });
  const openSubmissionList = (mode) => setSubmissionList({ isOpen: true, mode });
  const closeSubmissionList = () => setSubmissionList(prev => ({ ...prev, isOpen: false }));

  const { data: p = {}, isLoading, error } = useQuery({
    queryKey: ['problem', problem_code, contest_code],
    queryFn: () => fetchProblem(problem_code, contest_code),
    enabled: !!problem_code, // Chỉ chạy query khi có problem_code
    staleTime: 1000 * 60 * 5,
  });

  // Loading & Error states
  if (isLoading) {
    return (
      <div className="box has-text-centered">
        <p className="has-text-grey">Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="notification is-danger is-light">
        {error.response?.data?.detail || error.message || t("Cannot load problem")}
      </div>
    );
  }

  return (
    <div className="columns">
      {/* Left column: Function buttons and problem infos */}
      <div className="column is-one-fifth">
        <div className="buttons is-centered">
          <button 
            onClick={() => loginRequired(() => setIsSubmitModalOpen(true))} 
            className="button is-primary is-fullwidth"
          >
            Submit
          </button>
          <button 
            onClick={() => openSubmissionList('status')} 
            className="button is-info" 
            title='All submissions'
          >
            <i className="fas fa-signal"/>
          </button>
          <button 
            onClick={() => openSubmissionList('my-submissions')} 
            className="button is-info" 
            title='My submissions'
          >
            <i className="fas fa-user-circle"/>
          </button>
          <button 
            onClick={() => openSubmissionList('leaderboard')} 
            className="button is-link" 
            title='Leaderboard'
          >
            <i className="fas fa-crown"/>
          </button>
        </div>
        
        <div className="box">
          <p><strong>Time limit:</strong> {p.time_limit ? `${p.time_limit} ms` : 'N/A'}</p>
          <p><strong>Memory limit:</strong> {p.memory_limit ? `${(p.memory_limit / 1024).toFixed(1)} MB` : 'N/A'}</p>
          <p><strong>Input:</strong> {p.input || 'stdin'}</p>
          <p><strong>Output:</strong> {p.output || 'stdout'}</p>
          
          {p.authors && p.authors.length > 0 && (
            <div>
              <strong>{p.authors.length > 1 ? t('Authors') : t('Author')}: </strong>
              {p.authors.map((a, index) => (
                <React.Fragment key={a.id || index}>
                  {HandleDisplay(a)}
                  {index < p.authors.length - 1 && ', '}
                </React.Fragment>
              ))}
            </div>
          )}
        </div>
      </div>
      
      {/* Right column: Problem title and statement */}
      <div className="column">
        <h1 className="title">
          {p.name || ``}{' '}
          <span className="has-text-grey-light">({p.code || problem_code})</span>
        </h1>
        <hr />
        
        {/* Render Markdown + LaTeX */}
        <div className="content">
          <ReactMarkdown
            remarkPlugins={[remarkGfm, remarkMath]}
            rehypePlugins={[rehypeKatex]}
          >
            {p.statement || t('No statement')}
          </ReactMarkdown>
        </div>
      </div>

      {/* Modals */}
      <SubmitModal 
        isOpen={isSubmitModalOpen}
        onClose={() => setIsSubmitModalOpen(false)}
        problem_code={p.code || problem_code}
        problemName={p.name}
        contest_code={contest_code}
      />
      
      <SubmissionList 
        isOpen={submissionList.isOpen}
        onClose={closeSubmissionList}
        problem_code={p.code || problem_code}
        problem_name={p.name}
        contest_code={contest_code}
        mode={submissionList.mode}
        username={current_user?.username || ""}
      />
    </div>
  );
}