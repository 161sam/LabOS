const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

async function getCharges() {
  try {
    const res = await fetch(`${apiBase}/api/v1/charges`, { cache: 'no-store' });
    if (!res.ok) throw new Error('failed');
    return res.json();
  } catch {
    return [];
  }
}

export default async function ChargesPage() {
  const charges = await getCharges();
  return (
    <div className="card">
      <h1>Chargen</h1>
      <table className="table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Spezies</th>
            <th>Status</th>
            <th>Volumen</th>
          </tr>
        </thead>
        <tbody>
          {charges.map((charge: any) => (
            <tr key={charge.id}>
              <td>{charge.name}</td>
              <td>{charge.species}</td>
              <td>{charge.status}</td>
              <td>{charge.volume_l} L</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
