export default function Header() {
  return (
    <header className="bg-gradient-to-r from-emerald-600 to-cyan-600 text-white shadow-lg">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Carbon Market Intelligence</h1>
            <p className="text-emerald-100 mt-1">Global carbon credit market analysis & prediction</p>
          </div>
          <div className="text-right">
            <div className="text-sm text-emerald-100">Powered by ML & Data Analytics</div>
          </div>
        </div>
      </div>
    </header>
  )
}
