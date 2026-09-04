export default function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-mint"></div>
      <p className="mt-4 text-ivory-secondary">{message}</p>
    </div>
  )
}
