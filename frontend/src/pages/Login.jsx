import { useWeb3Auth } from "@web3auth/modal-react-hooks";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";
import logo from '../assets/logo.png';

function Login() {
    const { connect, isConnected } = useWeb3Auth();
    const navigate = useNavigate();

    useEffect(() => {
        if (isConnected) {
            navigate("/habits");
        }
    }, [isConnected, navigate]);

    const handleLogin = async () => {
        await connect();
    };

    return (
        <div className="fixed inset-0 w-screen h-screen overflow-hidden flex items-center justify-center">
            {/* Background Image */}
            <div
                className="absolute inset-0 z-0"
                style={{
                    backgroundImage: "url('/bg-login1.png')",
                    backgroundPosition: "center",
                    backgroundRepeat: "no-repeat",
                    filter: "brightness(0.7)",
                    objectFit: "cover",
                }}
            />

            {/* Content */}
            <div className="w-full max-w-md px-4 sm:px-0">
                <div className="bg-white/10 p-8 rounded-xl shadow-lg backdrop-blur-md border border-white/30">
                    <div>
                        <div className="flex justify-center mb-4">
                            <img src={logo} alt="HabiChain Logo" className="w-16 h-16" />
                        </div>
                        <h2 className="mt-2 text-center text-3xl text-sky-800">
                            Welcome to HabiChain
                        </h2>
                        <p className="mt-2 text-center text-md text-black text-italic">
                            Analyze your behavior and build habits with blockchain security.
                        </p>
                    </div>

                    <div className="mt-8 space-y-4">
                        <button
                            onClick={handleLogin}
                            className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-sky-600/90 hover:bg-sky-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-500 transition-all duration-200 transform hover:scale-105 shadow-md"
                        >
                            Connect with Social Account
                        </button>

                        <p className="text-center text-sm text-gray-500">
                            By connecting, you agree to our <a href="#" className="text-sky-600 hover:text-sky-800 hover:underline">Terms of Service</a> and <a href="#" className="text-sky-600 hover:text-sky-800 hover:underline">Privacy Policy</a>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Login; 