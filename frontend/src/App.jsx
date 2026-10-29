/**
 * Pantalla de entrada del portal familiar.
 * El representante consulta aquí las notas, la asistencia, los
 * comunicados y las mensualidades de sus hijos.
 */
export default function App() {
  return (
    <main className="min-h-screen bg-[#f8fafc] font-sans text-meadow-yale">
      <header className="bg-meadow-yale px-6 py-4 text-white">
        <p className="font-display text-2xl font-semibold">ProAula</p>
        <p className="text-sm text-meadow-lime">Portal familiar</p>
      </header>
      <section className="mx-auto mt-10 max-w-xl rounded-2xl bg-white p-6 shadow-sm">
        <h1 className="font-display text-xl">Acceso de familias</h1>
        <p className="mt-2 text-sm">
          Consulta las notas, la asistencia, los comunicados y las
          mensualidades de tus hijos.
        </p>
      </section>
    </main>
  )
}
