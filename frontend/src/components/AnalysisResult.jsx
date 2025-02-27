import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export function AnalysisResult() {
    const [analysis, setAnalysis] = useState(null)
    const navigate = useNavigate()

    useEffect(() => {
        const analysisResults = localStorage.getItem('analysisResults')

        if (!analysisResults) {
            navigate('/form')
            return
        }

        try {
            const parsedAnalysis = JSON.parse(analysisResults)
            setAnalysis(parsedAnalysis)
        } catch (error) {
            console.error('Error parsing analysis results:', error)
            navigate('/form')
        }
    }, [navigate])

    const handleContinue = () => {
        navigate('/habits')
    }

    if (!analysis) {
        return (
            <div className="flex justify-center items-center min-h-screen bg-gray-50">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
            </div>
        )
    }

    return (
        <div className="max-w-2xl mx-auto p-6 mt-8">
            <div className="bg-white rounded-lg shadow-lg p-8">
                <h2 className="text-2xl font-bold text-sky-800 mb-6">Your Behavioral Analysis</h2>

                <div className="prose prose-sky max-w-none">
                    <div className="bg-sky-50 rounded-lg p-6 mb-8">
                        <p className="text-gray-700 whitespace-pre-wrap">
                            {analysis.general_analysis}
                        </p>
                    </div>
                </div>

                <div className="mt-8 flex justify-end">
                    <button
                        onClick={handleContinue}
                        className="px-6 py-3 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors"
                    >
                        Continue to Habit Recommendations →
                    </button>
                </div>
            </div>
        </div>
    )
} 