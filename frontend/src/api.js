const API_URL = 'http://127.0.0.1:8000'

export async function checkWig(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_URL}/analyze`, {
    method: 'POST',
    body: formData,
  })

  let data
  try {
    data = await response.json()
  } catch {
    throw new Error('The AI court returned an unreadable response.')
  }

  if (!response.ok) {
    throw new Error(data.detail || 'The wig investigation failed.')
  }

  return data
}