import React, { useState } from 'react';
import { post_request } from '../../Request';
import { toast } from 'react-toastify';

export default function SubmitModal({ isOpen, onClose, problemId, problemName, contestCode }) {
  const [language, setLanguage] = useState('cpp');
  const [source, setSource] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!source.trim()) return toast.error("Vui lòng nhập mã nguồn trước khi nộp bài!");

    setSubmitting(true);
    try {
      const submitPath = contestCode
        ? `/problem/${problemId}/submit?contest=${encodeURIComponent(contestCode)}`
        : `/problem/${problemId}/submit`;
      const res = await post_request(submitPath, { language, source });
      
      if (res.status === 200) {
        toast.success("Nộp bài thành công!");
        setSource('');
        onClose();
      } else {
        toast.error(res.data?.detail || "Có lỗi xảy ra khi nộp bài!");
      }
    } catch {
      toast.error("Không thể kết nối đến máy chủ.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className={`modal ${isOpen ? "is-active" : ""}`}>
      <div className="modal-background" onClick={() => !submitting && onClose()}></div>
      <div className="modal-content">
        <div className="box">
          <h2 className="title is-4">Nộp bài: {problemName || `Bài ${problemCode}`}</h2>
          
          <form onSubmit={handleSubmit} className="is-flex is-flex-direction-column style={{ gap: '12px' }}">
            {/* Language */}
            <div>
              <label className="label mb-1">Ngôn ngữ</label>
              <div className="select is-fullwidth">
                <select value={language} onChange={(e) => setLanguage(e.target.value)} disabled={submitting}>
                  <option value="cpp">C++</option>
                  <option value="py">Python</option>
                  <option value="text">Plain Text</option>
                </select>
              </div>
            </div>

            {/* Source code */}
            <div>
              <label className="label mb-1">Mã nguồn</label>
              <textarea 
                className="textarea" rows="12" placeholder="Dán code của bạn vào đây..."
                value={source} onChange={(e) => setSource(e.target.value)} disabled={submitting}
                style={{ fontFamily: 'monospace' }}
              />
            </div>

            {/* Button */}
            <div className="buttons is-right mt-2">
              <button type="button" className="button" onClick={onClose} disabled={submitting}>Hủy</button>
              <button type="submit" className={`button is-primary ${submitting ? 'is-loading' : ''}`} disabled={submitting}>Nộp bài</button>
            </div>
          </form>

        </div>
      </div>
      <button className="modal-close is-large" aria-label="close" onClick={() => !submitting && onClose()}></button>
    </div>
  );
}