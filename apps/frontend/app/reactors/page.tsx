const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

async function getReactors() {
  try {
    const res = await fetch(`${apiBase}/api/v1/reactors`, { cache: 'no-store' });
    if (!res.ok) throw new Error('failed');
    return res.json();
  } catch {
    return [];
  }
}

export default async function ReactorsPage() {
  const reactors = await getReactors();
  return (
    <div className="card">
      <h1>Reaktoren</h1>
      <table className="table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Typ</th>
            <th>Status</th>
            <th>Volumen</th>
          </tr>
        </thead>
        <tbody>
          {reactors.map((reactor: any) => (
            <tr key={reactor.id}>
              <td>{reactor.name}</td>
              <td>{reactor.reactor_type}</td>
              <td>{reactor.status}</td>
              <td>{reactor.volume_l} L</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
