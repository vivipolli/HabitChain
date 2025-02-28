import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { analyzeBehavior, createViewingKey } from '../services/api'
import { useWeb3Auth } from '@web3auth/modal-react-hooks'

export function PatientForm() {
    const navigate = useNavigate()
    const { userEmail } = useWeb3Auth();

    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [formData, setFormData] = useState({
        behavior: '',
        antecedent: '',
        consequence: '',
        previousAttempts: ''
    })

    const generatePatientId = () => {
        const timestamp = Date.now()
        const email = userEmail || 'anonymous'
        const emailHash = btoa(email).replace(/[^a-zA-Z0-9]/g, '')
        return `${emailHash}-${timestamp}`
    }

    const handleChange = (e) => {
        const { name, value } = e.target
        setFormData(prevState => ({
            ...prevState,
            [name]: value
        }))
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError(null)

        try {
            const patientId = generatePatientId()
            localStorage.setItem('patientId', patientId)

            // Criar viewing key antes de enviar a análise
            await createViewingKey(patientId)

            const analysisData = {
                patient_id: patientId,
                behavior: formData.behavior,
                antecedent: formData.antecedent,
                consequence: formData.consequence,
                previous_attempts: formData.previousAttempts
            }

            const response = await analyzeBehavior(analysisData)

            if (response.analysis) {
                // Salvar com a chave correta 'analysisResults'
                localStorage.setItem('analysisResults', JSON.stringify(response.analysis))

                // Também salvar no histórico de análises do paciente
                const storedAnalyses = JSON.parse(
                    localStorage.getItem(`analyses_${patientId}`) || '[]'
                )
                storedAnalyses.push(response.analysis)
                localStorage.setItem(
                    `analyses_${patientId}`,
                    JSON.stringify(storedAnalyses)
                )

                navigate('/analysis')
            } else {
                throw new Error('No analysis results received')
            }
        } catch (error) {
            console.error('Error in form submission:', error)
            setError('Failed to analyze behavior. Please try again.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <form onSubmit={handleSubmit} className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg text-left">
            <h2 className="text-2xl font-bold text-sky-800 mb-6">Behavioral Analysis Form</h2>

            <div className="mb-8">
                <h3 className="text-xl font-semibold text-sky-700 mb-4">Section 1: Behavior Analysis</h3>

                <div className="mb-4">
                    <label className="block text-gray-700 font-medium mb-2">
                        1. Behavior - What behavior would you like to analyze?
                        <span className="text-sm text-gray-500 block">Be specific and describe what you do, think, or feel.</span>
                    </label>
                    <textarea
                        name="behavior"
                        value={formData.behavior}
                        onChange={handleChange}
                        className="w-full p-2 border border-gray-300 rounded-md focus:ring-sky-500 focus:border-sky-500"
                        rows="3"
                        placeholder="Example: 'Nail biting when I'm nervous.'"
                    />
                </div>

                <div className="mb-4">
                    <label className="block text-gray-700 font-medium mb-2">
                        2. Antecedent - In what situations, environments, or moments does this behavior occur most frequently?
                        <span className="text-sm text-gray-500 block">Provide a concrete example.</span>
                    </label>
                    <textarea
                        name="antecedent"
                        value={formData.antecedent}
                        onChange={handleChange}
                        className="w-full p-2 border border-gray-300 rounded-md focus:ring-sky-500 focus:border-sky-500"
                        rows="3"
                        placeholder="Example: 'When working on a difficult project, waiting in line, or watching TV feeling anxious.'"
                    />
                </div>

                <div className="mb-4">
                    <label className="block text-gray-700 font-medium mb-2">
                        3. Consequence - What happens after you exhibit this behavior and what benefits do you feel?
                        <span className="text-sm text-gray-500 block">Describe both immediate and long-term consequences.</span>
                    </label>
                    <textarea
                        name="consequence"
                        value={formData.consequence}
                        onChange={handleChange}
                        className="w-full p-2 border border-gray-300 rounded-md focus:ring-sky-500 focus:border-sky-500"
                        rows="3"
                        placeholder="Example: 'I feel momentary relief from anxiety, but later feel guilty and ashamed about biting my nails.'"
                    />
                </div>
            </div>

            <div className="mb-8">
                <h3 className="text-xl font-semibold text-sky-700 mb-4">Section 2: Coping Strategies</h3>

                <div className="mb-4">
                    <label className="block text-gray-700 font-medium mb-2">
                        1. Have you tried any ways to deal with this behavior? If so, what did you do?
                    </label>
                    <textarea
                        name="previousAttempts"
                        value={formData.previousAttempts}
                        onChange={handleChange}
                        className="w-full p-2 border border-gray-300 rounded-md focus:ring-sky-500 focus:border-sky-500"
                        rows="3"
                        placeholder="Example: 'I tried using bitter nail polish but it didn't work. I also tried keeping my hands busy with a stress ball, but that didn't help either.'"
                    />
                </div>
            </div>

            {error && (
                <div className="mb-4 p-4 bg-red-50 text-red-700 rounded-md">
                    {error}
                </div>
            )}

            <button
                type="submit"
                disabled={loading}
                className={`w-full py-2 px-4 rounded-lg transition-colors shadow-sm flex items-center justify-center space-x-2
                    ${loading
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-sky-600 hover:bg-sky-700 text-white'}`}
            >
                {loading && (
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                )}
                <span>{loading ? 'Analyzing...' : 'Submit Analysis'}</span>
            </button>
        </form>
    )
} 