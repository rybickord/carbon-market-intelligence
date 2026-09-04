export default function ErrorMessage({ message }) {
  return (
    <div className="bg-negative/10 border border-negative/30 rounded-lg p-6">
      <div className="flex items-start">
        <svg className="w-6 h-6 text-negative flex-shrink-0 mr-3" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
          <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <h3 className="text-negative font-semibold">Error Loading Data</h3>
          <p className="text-ivory-secondary mt-1 text-sm">{message}</p>
        </div>
      </div>
    </div>
  )
}
