import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Example as AnimatedCheck } from './AnimatedCheck'
import { getAnalyses } from '../services/api'

export function HabitsTracker() {
    const navigate = useNavigate()
    const [habits, setHabits] = useState([])
    const [expandedHabit, setExpandedHabit] = useState(null)
    const [selectedDay, setSelectedDay] = useState(new Date().getDay())
    const [dailyReflections, setDailyReflections] = useState({})
    const [isReflectionExpanded, setIsReflectionExpanded] = useState(false)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        async function fetchAnalysis() {
            try {
                const patientId = localStorage.getItem('patientId')
                const viewingKey = localStorage.getItem('viewingKey')

                if (!patientId || !viewingKey) {
                    navigate('/form')
                    return
                }

                const response = await getAnalyses(patientId, viewingKey)

                if (!response.analyses || response.analyses.length === 0) {
                    navigate('/form')
                    return
                }

                const latestAnalysis = response.analyses[response.analyses.length - 1]

                let parsedContent
                try {
                    parsedContent = JSON.parse(latestAnalysis.content)
                } catch (err) {
                    console.error('Error parsing analysis content:', err)
                    setError('Invalid analysis format')
                    return
                }

                if (!parsedContent.recommended_habits || parsedContent.recommended_habits.length === 0) {
                    setError('No habits recommendations found')
                    return
                }

                const formattedHabits = parsedContent.recommended_habits.map((habit, index) => ({
                    id: index + 1,
                    title: habit.name || 'Unnamed Habit',
                    description: habit.description || 'No description available',
                    details: Array.isArray(habit.implementation)
                        ? habit.implementation.join('\n')
                        : 'No implementation steps available',
                    reference: habit.scientific_basis
                        ? { title: habit.scientific_basis }
                        : null,
                    daysCompleted: []
                }))

                setHabits(formattedHabits)
                setError(null)
            } catch (err) {
                console.error('Error fetching analysis:', err)
                setError('Failed to load habits. Please try again later.')
            } finally {
                setLoading(false)
            }
        }

        fetchAnalysis()
    }, [navigate])

    const daysOfWeek = [
        { name: 'Sun', index: 0 },
        { name: 'Mon', index: 1 },
        { name: 'Tue', index: 2 },
        { name: 'Wed', index: 3 },
        { name: 'Thu', index: 4 },
        { name: 'Fri', index: 5 },
        { name: 'Sat', index: 6 }
    ]

    const currentDay = new Date().getDay()
    const isCurrentDay = selectedDay === currentDay

    const toggleHabit = (habitId) => {
        setHabits(habits.map(habit => {
            if (habit.id === habitId) {
                const newDaysCompleted = habit.daysCompleted.includes(selectedDay)
                    ? habit.daysCompleted.filter(d => d !== selectedDay)
                    : [...habit.daysCompleted, selectedDay]
                return { ...habit, daysCompleted: newDaysCompleted }
            }
            return habit
        }))
    }

    const isCheckboxDisabled = (dayIndex) => {
        return dayIndex > currentDay
    }

    const handleReflectionChange = (e) => {
        setDailyReflections({
            ...dailyReflections,
            [selectedDay]: e.target.value
        })
    }

    const calculateDailyProgress = () => {
        const completedHabits = habits.filter(habit =>
            habit.daysCompleted.includes(selectedDay)
        ).length
        const totalHabits = habits.length
        const percentage = (completedHabits / totalHabits) * 100
        return Math.round(percentage)
    }

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen p-6">
                <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-sky-600 mb-4"></div>
                <p className="text-sky-800 font-medium">Loading your habits tracker...</p>
            </div>
        )
    }

    if (error) {
        return (
            <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg text-left">
                <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                    <h3 className="text-lg font-medium text-red-800 mb-2">Error Loading Habits</h3>
                    <p className="text-red-700">{error}</p>
                    <button
                        onClick={() => navigate('/form')}
                        className="mt-4 px-4 py-2 bg-sky-600 text-white rounded-md hover:bg-sky-700 transition-colors"
                    >
                        Return to Form
                    </button>
                </div>
            </div>
        )
    }

    return (
        <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg text-left">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-sky-800">Suggested Habits Tracker</h2>
                <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600">Daily Progress:</span>
                    <span className={`font-semibold ${calculateDailyProgress() === 100
                        ? 'text-green-500'
                        : calculateDailyProgress() >= 50
                            ? 'text-sky-600'
                            : 'text-gray-700'
                        }`}>
                        {calculateDailyProgress()}%
                    </span>
                </div>
            </div>

            <div className="flex justify-between items-center mb-8 border-b pb-4">
                <div className="flex space-x-2">
                    {daysOfWeek.map((day) => (
                        <button
                            key={day.index}
                            onClick={() => setSelectedDay(day.index)}
                            disabled={isCheckboxDisabled(day.index)}
                            className={`
                                px-4 py-2 rounded-lg transition-colors
                                ${selectedDay === day.index ? 'bg-sky-600 text-white' : 'bg-gray-100 text-gray-700'}
                                ${isCheckboxDisabled(day.index) ? 'opacity-50 cursor-not-allowed' : 'hover:bg-sky-500 hover:text-white'}
                            `}
                        >
                            {day.name}
                        </button>
                    ))}
                </div>
            </div>

            <div className="space-y-4">
                {habits.map(habit => (
                    <div
                        key={habit.id}
                        className={`border rounded-lg p-4 transition-all duration-300 ${habit.daysCompleted.includes(selectedDay)
                            ? 'bg-sky-50 border-sky-600'
                            : 'border-gray-200'
                            }`}
                    >
                        <div className="flex items-start space-x-4">
                            <div className="flex items-center">
                                <AnimatedCheck
                                    isChecked={habit.daysCompleted.includes(selectedDay)}
                                    onCheck={() => toggleHabit(habit.id)}
                                />
                            </div>
                            <div className="flex-1">
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h3 className="font-medium text-sky-800">{habit.title}</h3>
                                        <p className="text-sm text-gray-600">{habit.description}</p>
                                    </div>
                                    <button
                                        onClick={() => setExpandedHabit(expandedHabit === habit.id ? null : habit.id)}
                                        className="text-sm text-sky-600 hover:text-sky-700"
                                    >
                                        {expandedHabit === habit.id ? 'Show less' : 'Learn more'}
                                    </button>
                                </div>

                                {expandedHabit === habit.id && (
                                    <div className="mt-3 space-y-3">
                                        <div className="p-3 bg-sky-50 rounded-md">
                                            <p className="text-sm text-gray-700">{habit.details}</p>
                                        </div>
                                        {habit.reference && (
                                            <div className="p-3 bg-gray-50 rounded-md">
                                                <p className="text-xs text-gray-500 mb-1">Scientific Reference:</p>
                                                <a
                                                    href={habit.reference.url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="text-sm text-sky-600 hover:text-sky-800 hover:underline"
                                                >
                                                    {habit.reference.title}
                                                </a>
                                                <p className="text-xs text-gray-500 mt-1">
                                                    Published in: {habit.reference.publisher}
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            <div className="mt-8 border-t border-gray-200 pt-6">
                <button
                    onClick={() => setIsReflectionExpanded(!isReflectionExpanded)}
                    className="w-full flex items-center justify-between text-left mb-4"
                >
                    <div className="flex items-center gap-2">
                        <h3 className="text-lg font-medium text-sky-800">Evening Reflection</h3>
                        <span className="text-sm text-gray-500">
                            {isCurrentDay && "(Fill this in before going to bed tonight)"}
                        </span>
                    </div>
                    <svg
                        className={`w-5 h-5 text-sky-600 transform transition-transform duration-300 ease-in-out ${isReflectionExpanded ? 'rotate-180' : ''
                            }`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M19 9l-7 7-7-7"
                        />
                    </svg>
                </button>

                <div className={`transition-all duration-300 ease-in-out overflow-hidden ${isReflectionExpanded ? 'max-h-[1000px] opacity-100' : 'max-h-0 opacity-0'
                    }`}>
                    <div className="bg-gray-50 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                            <label className="block text-gray-700 font-medium">
                                How did you feel today?
                            </label>
                            {isCurrentDay && (
                                <span className="text-sm text-sky-600">
                                    🌙 Complete this before bedtime
                                </span>
                            )}
                        </div>
                        <textarea
                            value={dailyReflections[selectedDay] || ''}
                            onChange={handleReflectionChange}
                            disabled={!isCurrentDay}
                            placeholder={isCurrentDay
                                ? "Take a moment before bed to reflect on your day. How did your habits impact your well-being today?"
                                : "This reflection should have been completed at the end of this day"
                            }
                            className={`w-full p-3 border rounded-md focus:ring-sky-500 focus:border-sky-500
                                ${!isCurrentDay ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}
                            `}
                            rows="4"
                        />
                        {isCurrentDay && (
                            <div className="mt-2 p-3 bg-sky-50 rounded-md">
                                <p className="text-sm text-sky-800">
                                    <span className="font-medium">✨ Evening Reflection Tip:</span>
                                    <br />
                                    Taking a few minutes before bed to reflect on your day helps:
                                </p>
                                <ul className="mt-2 text-sm text-sky-700 list-disc list-inside">
                                    <li>Process your daily experiences</li>
                                    <li>Recognize your achievements</li>
                                    <li>Identify areas for improvement</li>
                                    <li>Set intentions for tomorrow</li>
                                </ul>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
} 