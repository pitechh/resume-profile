import React, { useEffect, useState } from 'react';
import { FaHistory, FaSave, FaUndo, FaSpinner } from 'react-icons/fa';
import { portfolioStorageService } from '../services/api';

interface SnapshotPanelProps {
  profileId?: number;
  getCurrentData: () => unknown;
  onRestore: (data: any) => void;
  accent?: 'orange' | 'blue';
}

/**
 * SnapshotPanel — Lưu / khôi phục hồ sơ qua backend Node (file JSON, không DB).
 * Backend: POST / GET /api/v1/storage/portfolio/{profileId}
 */
const SnapshotPanel: React.FC<SnapshotPanelProps> = ({
  profileId,
  getCurrentData,
  onRestore,
  accent = 'orange',
}) => {
  const [versions, setVersions] = useState<Array<{ id: string; updatedAt: string }>>([]);
  const [saving, setSaving] = useState(false);
  const [restoring, setRestoring] = useState(false);
  const [available, setAvailable] = useState(true);
  const [message, setMessage] = useState('');

  const btn = accent === 'orange'
    ? 'bg-orange-500 hover:bg-orange-600'
    : 'bg-blue-600 hover:bg-blue-700';

  const loadVersions = async () => {
    if (!profileId) return;
    try {
      const res = await portfolioStorageService.listVersions(profileId);
      setVersions(res.versions || []);
      setAvailable(true);
    } catch {
      setAvailable(false);
    }
  };

  useEffect(() => {
    loadVersions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [profileId]);

  const handleSave = async () => {
    if (!profileId) {
      alert('Không xác định được Profile ID!');
      return;
    }
    setSaving(true);
    setMessage('');
    try {
      const res = await portfolioStorageService.saveSnapshot(profileId, getCurrentData());
      setMessage(`✅ Đã lưu bản snapshot lúc ${res.version}`);
      await loadVersions();
    } catch {
      setAvailable(false);
      alert('❌ Không lưu được snapshot. Hãy chắc backend Node đang chạy (cd backend && npm start).');
    } finally {
      setSaving(false);
    }
  };

  const handleRestore = async () => {
    if (!profileId) return;
    if (!confirm('Khôi phục bản snapshot mới nhất? Nội dung đang sửa sẽ bị thay thế.')) return;
    setRestoring(true);
    setMessage('');
    try {
      const data = await portfolioStorageService.getSnapshot(profileId);
      // Bóc lớp _meta của backend trước khi đổ vào form
      const { _meta, ...clean } = data as any;
      onRestore(clean);
      setMessage('✅ Đã khôi phục bản mới nhất vào form. Nhấn Save để ghi lên server chính.');
    } catch {
      setAvailable(false);
      alert('❌ Chưa có bản snapshot nào hoặc backend chưa chạy.');
    } finally {
      setRestoring(false);
    }
  };

  if (!available) {
    return (
      <div className="mt-6 p-4 rounded-xl border border-dashed border-gray-300 bg-gray-50 text-sm text-gray-500">
        <span className="font-bold">💾 Snapshot hồ sơ (backend Node):</span>{' '}
        chưa kết nối được — chạy <code className="bg-gray-200 px-1 rounded">cd backend && npm start</code> để bật.
      </div>
    );
  }

  return (
    <div className="mt-6 p-4 rounded-xl border bg-gray-50 space-y-3">
      <div className="flex items-center gap-2 font-bold text-sm">
        <FaHistory /> Snapshot hồ sơ (lưu file JSON, không cần DB)
        <span className="ml-auto text-xs font-normal text-gray-500">
          {versions.length} bản đã lưu
        </span>
      </div>
      <div className="flex flex-wrap gap-2">
        <button
          onClick={handleSave}
          disabled={saving}
          className={`${btn} text-white px-4 py-2 rounded font-bold text-sm disabled:opacity-50`}
        >
          {saving ? <FaSpinner className="inline mr-2 animate-spin" /> : <FaSave className="inline mr-2" />}
          Lưu snapshot
        </button>
        <button
          onClick={handleRestore}
          disabled={restoring || versions.length === 0}
          className="bg-gray-600 text-white px-4 py-2 rounded font-bold text-sm hover:bg-gray-700 disabled:opacity-50"
        >
          {restoring ? <FaSpinner className="inline mr-2 animate-spin" /> : <FaUndo className="inline mr-2" />}
          Khôi phục bản mới nhất
        </button>
      </div>
      {versions.length > 0 && (
        <div className="text-xs text-gray-500 max-h-24 overflow-y-auto">
          {versions.slice(-5).reverse().map((v) => (
            <div key={v.id} className="font-mono truncate">
              • {v.id} <span className="text-gray-400">({v.updatedAt})</span>
            </div>
          ))}
        </div>
      )}
      {message && <div className="text-xs text-green-700">{message}</div>}
    </div>
  );
};

export default SnapshotPanel;
