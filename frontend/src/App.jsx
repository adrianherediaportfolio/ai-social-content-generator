import { useState, useEffect } from 'react'

const API_BASE = '/api/v1'

function PlatformBadge({ platform }) {
  const colors = {
    twitter: 'bg-blue-100 text-blue-800',
    linkedin: 'bg-sky-100 text-sky-800',
    instagram: 'bg-pink-100 text-pink-800',
  }
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${colors[platform] || 'bg-gray-100 text-gray-800'}`}>
      {platform}
    </span>
  )
}

function StatusBadge({ status }) {
  const colors = {
    draft: 'bg-gray-100 text-gray-700',
    scheduled: 'bg-yellow-100 text-yellow-800',
    published: 'bg-green-100 text-green-800',
  }
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${colors[status] || 'bg-gray-100'}`}>
      {status}
    </span>
  )
}

function GenerateForm({ onGenerated }) {
  const [topic, setTopic] = useState('')
  const [sourceUrl, setSourceUrl] = useState('')
  const [platforms, setPlatforms] = useState(['twitter', 'linkedin', 'instagram'])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const togglePlatform = (p) => {
    setPlatforms(prev => prev.includes(p) ? prev.filter(x => x !== p) : [...prev, p])
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!topic.trim() || platforms.length === 0) return
    setLoading(true)
    setResult(null)
    try {
      const res = await fetch(`${API_BASE}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: topic.trim(), source_url: sourceUrl.trim(), platforms }),
      })
      const data = await res.json()
      setResult(data)
      onGenerated()
    } catch (err) {
      setResult({ success: false, error: err.message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h2 className="text-lg font-semibold mb-4">Generate Content</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Topic *</label>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g., AI trends in 2026, New React features..."
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Source URL (optional)</label>
          <input
            type="url"
            value={sourceUrl}
            onChange={(e) => setSourceUrl(e.target.value)}
            placeholder="https://..."
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Platforms</label>
          <div className="flex gap-3">
            {['twitter', 'linkedin', 'instagram'].map(p => (
              <button
                key={p}
                type="button"
                onClick={() => togglePlatform(p)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                  platforms.includes(p)
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {p.charAt(0).toUpperCase() + p.slice(1)}
              </button>
            ))}
          </div>
        </div>
        <button
          type="submit"
          disabled={loading || !topic.trim() || platforms.length === 0}
          className="w-full py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
        >
          {loading ? 'Generating...' : 'Generate Content'}
        </button>
      </form>

      {result && result.success && (
        <div className="mt-6 space-y-4">
          <h3 className="font-medium text-green-700">Generated {result.posts.length} posts!</h3>
          {result.posts.map((post, i) => (
            <div key={i} className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <PlatformBadge platform={post.platform} />
                <span className="text-xs text-gray-500">{post.character_count} chars</span>
              </div>
              <p className="text-sm whitespace-pre-wrap">{post.content}</p>
              {post.hashtags.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {post.hashtags.map((tag, j) => (
                    <span key={j} className="text-xs text-blue-600">#{tag}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function PostList({ posts, onRefresh }) {
  const handleDelete = async (id) => {
    await fetch(`${API_BASE}/posts/${id}`, { method: 'DELETE' })
    onRefresh()
  }

  if (posts.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border p-8 text-center text-gray-500">
        No posts yet. Generate some content to get started!
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {posts.map(post => (
        <div key={post.id} className="bg-white rounded-xl shadow-sm border p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <PlatformBadge platform={post.platform} />
              <StatusBadge status={post.status} />
            </div>
            <button
              onClick={() => handleDelete(post.id)}
              className="text-red-400 hover:text-red-600 text-sm"
            >
              Delete
            </button>
          </div>
          <p className="text-sm text-gray-700 mb-1 font-medium">{post.topic}</p>
          <p className="text-sm text-gray-600 whitespace-pre-wrap line-clamp-3">{post.content}</p>
          {post.hashtags && post.hashtags.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {post.hashtags.map((tag, j) => (
                <span key={j} className="text-xs text-blue-600">#{tag}</span>
              ))}
            </div>
          )}
          <div className="mt-2 text-xs text-gray-400">
            {post.created_at}
            {post.scheduled_at && ` · Scheduled: ${post.scheduled_at}`}
          </div>
        </div>
      ))}
    </div>
  )
}

function StatsBar({ stats }) {
  return (
    <div className="grid grid-cols-4 gap-4">
      {[
        { label: 'Total', value: stats.total, color: 'text-gray-900' },
        { label: 'Drafts', value: stats.draft, color: 'text-gray-600' },
        { label: 'Scheduled', value: stats.scheduled, color: 'text-yellow-600' },
        { label: 'Published', value: stats.published, color: 'text-green-600' },
      ].map(({ label, value, color }) => (
        <div key={label} className="bg-white rounded-xl shadow-sm border p-4 text-center">
          <div className={`text-2xl font-bold ${color}`}>{value}</div>
          <div className="text-sm text-gray-500">{label}</div>
        </div>
      ))}
    </div>
  )
}

export default function App() {
  const [posts, setPosts] = useState([])
  const [stats, setStats] = useState({ total: 0, draft: 0, scheduled: 0, published: 0 })
  const [filter, setFilter] = useState({ platform: '', status: '' })

  const fetchPosts = async () => {
    const params = new URLSearchParams()
    if (filter.platform) params.set('platform', filter.platform)
    if (filter.status) params.set('status', filter.status)
    const res = await fetch(`${API_BASE}/posts?${params}`)
    setPosts(await res.json())
  }

  const fetchStats = async () => {
    const res = await fetch(`${API_BASE}/stats`)
    setStats(await res.json())
  }

  const refresh = () => { fetchPosts(); fetchStats() }

  useEffect(() => { refresh() }, [filter])

  return (
    <div className="min-h-screen">
      <header className="bg-white border-b">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <h1 className="text-xl font-bold text-gray-900">AI Social Content Generator</h1>
          <p className="text-sm text-gray-500">Generate, schedule, and manage social media content with AI</p>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-6 space-y-6">
        <StatsBar stats={stats} />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <GenerateForm onGenerated={refresh} />

          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Posts</h2>
              <div className="flex gap-2">
                <select
                  value={filter.platform}
                  onChange={(e) => setFilter(f => ({ ...f, platform: e.target.value }))}
                  className="text-sm border rounded-lg px-2 py-1"
                >
                  <option value="">All platforms</option>
                  <option value="twitter">Twitter</option>
                  <option value="linkedin">LinkedIn</option>
                  <option value="instagram">Instagram</option>
                </select>
                <select
                  value={filter.status}
                  onChange={(e) => setFilter(f => ({ ...f, status: e.target.value }))}
                  className="text-sm border rounded-lg px-2 py-1"
                >
                  <option value="">All status</option>
                  <option value="draft">Draft</option>
                  <option value="scheduled">Scheduled</option>
                  <option value="published">Published</option>
                </select>
              </div>
            </div>
            <PostList posts={posts} onRefresh={refresh} />
          </div>
        </div>
      </main>
    </div>
  )
}
