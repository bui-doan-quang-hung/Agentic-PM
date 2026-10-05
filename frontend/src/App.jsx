import { useCallback, useEffect, useState } from 'react';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const priorities = ['LOW', 'MEDIUM', 'HIGH'];
const statuses = ['TODO', 'DOING', 'DONE'];
const emptyForm = { title: '', content: '', priority: 'MEDIUM' };

export default function App() {
  const [notes, setNotes] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editing, setEditing] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const loadNotes = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/notes`);
      if (!response.ok) throw new Error('Could not load notes.');
      setNotes(await response.json());
      setError('');
    } catch (err) {
      setError(err.message || 'Could not connect to the API.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadNotes(); }, [loadNotes]);

  async function submit(event) {
    event.preventDefault();
    setError('');
    try {
      const response = await fetch(editing ? `${API}/api/notes/${editing}` : `${API}/api/notes`, {
        method: editing ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.detail?.[0]?.msg || 'Could not save note.');
      }
      setForm(emptyForm);
      setEditing(null);
      await loadNotes();
    } catch (err) { setError(err.message); }
  }

  function startEdit(note) {
    setEditing(note.id);
    setForm({ title: note.title, content: note.content || '', priority: note.priority });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  async function changeStatus(id, status) {
    setError('');
    try {
      const response = await fetch(`${API}/api/notes/${id}/status`, {
        method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status }),
      });
      if (!response.ok) throw new Error('Could not change status.');
      await loadNotes();
    } catch (err) { setError(err.message); }
  }

  async function removeNote(id) {
    setError('');
    try {
      const response = await fetch(`${API}/api/notes/${id}`, { method: 'DELETE' });
      if (!response.ok) throw new Error('Could not delete note.');
      if (editing === id) cancelEdit();
      await loadNotes();
    } catch (err) { setError(err.message); }
  }

  function cancelEdit() { setEditing(null); setForm(emptyForm); }

  return (
    <main className="page-shell">
      <header className="hero">
        <div className="brand-mark" aria-hidden="true">✳</div>
        <div><p className="eyebrow">A LITTLE SPACE FOR YOUR THOUGHTS</p><h1>Sticky Notes</h1></div>
        <span className="note-count">{notes.length} {notes.length === 1 ? 'note' : 'notes'}</span>
      </header>

      {error && <div className="error-banner" role="alert">{error}</div>}

      <section className="composer panel">
        <div className="section-heading"><div><p className="eyebrow">{editing ? 'MAKE IT JUST RIGHT' : 'GET IT OUT OF YOUR HEAD'}</p><h2>{editing ? 'Edit note' : 'New note'}</h2></div><span className="sparkle">✦</span></div>
        <form onSubmit={submit}>
          <label className="field-label" htmlFor="title">Title</label>
          <input id="title" maxLength="255" required placeholder="Give this thought a name…" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          <label className="field-label" htmlFor="content">A few more details <span className="optional">(optional)</span></label>
          <textarea id="content" rows="3" placeholder="Add a little context…" value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} />
          <div className="form-footer"><label className="priority-picker"><span className="field-label">Priority</span><select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}>{priorities.map((item) => <option key={item}>{item}</option>)}</select></label><div className="form-actions">{editing && <button className="button quiet" type="button" onClick={cancelEdit}>Cancel</button>}<button className="button primary" type="submit">{editing ? 'Save changes' : 'Add note'} <span aria-hidden="true">↗</span></button></div></div>
        </form>
      </section>

      <section className="notes-section">
        <div className="section-heading list-heading"><div><p className="eyebrow">YOUR THOUGHTS, IN ONE PLACE</p><h2>Notes <span className="heading-count">{notes.length.toString().padStart(2, '0')}</span></h2></div><button className="refresh-button" onClick={loadNotes} aria-label="Refresh notes">↻ <span>Refresh</span></button></div>
        {loading ? <p className="empty-state">Gathering your notes…</p> : notes.length === 0 ? <div className="empty-state"><span>✳</span><p>Nothing pinned just yet.</p><small>Add a note above and it’ll find its place here.</small></div> : <div className="notes-grid">{notes.map((note, index) => <article className={`note-card tone-${index % 4}`} key={note.id}>
          <div className="card-topline"><span className={`priority-badge priority-${note.priority.toLowerCase()}`}><i />{note.priority}</span><button className="delete-button" onClick={() => removeNote(note.id)} aria-label={`Delete ${note.title}`}>×</button></div>
          <h3>{note.title}</h3>{note.content && <p className="note-content">{note.content}</p>}
          <div className="card-bottom"><label className="status-control"><span>Status</span><select aria-label={`Status for ${note.title}`} value={note.status} onChange={(e) => changeStatus(note.id, e.target.value)}>{statuses.map((status) => <option key={status}>{status}</option>)}</select></label><button className="edit-button" onClick={() => startEdit(note)}>Edit <span>↗</span></button></div>
        </article>)}</div>}
      </section>
      <footer>MADE FOR THE THINGS YOU DON’T WANT TO FORGET <span>✳</span></footer>
    </main>
  );
}
