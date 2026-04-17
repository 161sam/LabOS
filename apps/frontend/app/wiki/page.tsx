const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

async function getWikiPages() {
  try {
    const res = await fetch(`${apiBase}/api/v1/wiki/pages`, { cache: 'no-store' });
    if (!res.ok) throw new Error('failed');
    return res.json();
  } catch {
    return [];
  }
}

export default async function WikiPage() {
  const pages = await getWikiPages();
  return (
    <div className="card">
      <h1>Wiki</h1>
      <ul>
        {pages.map((page: any) => (
          <li key={page.slug}><strong>{page.title}</strong> — {page.slug}</li>
        ))}
      </ul>
    </div>
  );
}
