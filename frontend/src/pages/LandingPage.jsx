import React from 'react';
import { Link } from 'react-router-dom';
import {
    ArrowRight,
    Layers,
    Calculator,
    Clock,
    Brain,
    Database,
    ShieldCheck,
    FileText,
    Gavel,
    Scroll,
    Pickaxe,
    Coins
} from 'lucide-react';

const LandingPage = () => {
    return (
        <div className="min-h-screen bg-zinc-50 text-zinc-900 font-sans selection:bg-indigo-100 selection:text-indigo-900">

            {/* Navbar / Header */}
            <nav className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className="h-8 w-8 bg-zinc-900 rounded-lg flex items-center justify-center">
                        <Layers className="h-5 w-5 text-white" />
                    </div>
                    <span className="text-lg font-bold tracking-tight text-zinc-900">AssetOS</span>
                </div>
                <div className="hidden md:flex items-center gap-6">
                    <Link to="/app" className="text-sm font-medium text-zinc-600 hover:text-zinc-900 transition-colors">
                        Log in
                    </Link>
                    <Link
                        to="/app"
                        className="text-sm font-medium bg-zinc-900 text-white px-4 py-2 rounded-md hover:bg-zinc-800 transition-colors"
                    >
                        Launch Demo
                    </Link>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="pt-24 pb-20 px-6 text-center max-w-5xl mx-auto">
                <h1 className="text-5xl md:text-6xl font-bold tracking-tight text-zinc-900 mb-8 leading-[1.1]">
                    The Operating System for <br className="hidden md:block" />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-zinc-900 to-zinc-600">
                        Special Situations Investing.
                    </span>
                </h1>
                <p className="text-xl text-zinc-600 max-w-2xl mx-auto mb-10 leading-relaxed">
                    One platform to manage Tax Liens, Judgments, Probate, Minerals,
                    and Surplus Funds. Stop context-switching across 5 different systems.
                </p>
                <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                    <Link
                        to="/app"
                        className="group inline-flex items-center gap-2 bg-indigo-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-indigo-700 transition-all shadow-sm hover:shadow-md"
                    >
                        Try the live demo
                        <ArrowRight className="h-4 w-4 group-hover:translate-x-0.5 transition-transform" />
                    </Link>
                    <a
                        href="https://github.com/3piecechickendinner/LeinOS"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center text-zinc-600 px-8 py-4 rounded-lg text-lg font-medium hover:text-zinc-900 border border-transparent hover:border-zinc-200 transition-all"
                    >
                        View on GitHub
                    </a>
                </div>
            </section>

            {/* Problem Statement */}
            <section className="py-20 px-6 bg-white border-y border-zinc-100">
                <div className="max-w-3xl mx-auto text-center">
                    <h2 className="text-xs font-bold uppercase tracking-wider text-indigo-600 mb-4">The Current Reality</h2>
                    <h3 className="text-3xl font-semibold text-zinc-900 mb-8">
                        5 Excel trackers. 3 separate CRMs. 2 manual deadline calendars.
                    </h3>
                    <p className="text-lg text-zinc-600 mb-8 leading-relaxed">
                        Your analysts spend 15 hours per week reconciling data across systems.
                        One missed redemption deadline = <span className="font-semibold text-zinc-900">$50K in lost returns</span>.
                        One statute expiration = entire judgment worthless.
                    </p>
                    <p className="text-lg text-zinc-900 font-medium">
                        Special situations investing requires precision. Your tools shouldn't add complexity.
                    </p>
                </div>
            </section>

            {/* Feature Grid */}
            <section className="py-24 px-6 max-w-7xl mx-auto">
                <div className="grid md:grid-cols-3 gap-12">
                    {/* Column 1 */}
                    <div className="space-y-4">
                        <div className="h-10 w-10 bg-zinc-100 rounded-lg flex items-center justify-center mb-2">
                            <Layers className="h-5 w-5 text-zinc-700" />
                        </div>
                        <h3 className="text-xl font-bold text-zinc-900">Unified Asset Tracking</h3>
                        <p className="text-zinc-600 leading-relaxed">
                            One dashboard for liens, judgments, minerals, probate, and surplus funds.
                            Real-time sync across all verticals without manual reconciliation.
                        </p>
                    </div>

                    {/* Column 2 */}
                    <div className="space-y-4">
                        <div className="h-10 w-10 bg-zinc-100 rounded-lg flex items-center justify-center mb-2">
                            <Calculator className="h-5 w-5 text-zinc-700" />
                        </div>
                        <h3 className="text-xl font-bold text-zinc-900">Automated Interest Calculation</h3>
                        <p className="text-zinc-600 leading-relaxed">
                            Polymorphic engine handles statutory interest, penalty rates, and royalty decimals.
                            Jurisdiction-specific rules applied automatically.
                        </p>
                    </div>

                    {/* Column 3 */}
                    <div className="space-y-4">
                        <div className="h-10 w-10 bg-zinc-100 rounded-lg flex items-center justify-center mb-2">
                            <Clock className="h-5 w-5 text-zinc-700" />
                        </div>
                        <h3 className="text-xl font-bold text-zinc-900">Intelligent Deadline Monitoring</h3>
                        <p className="text-zinc-600 leading-relaxed">
                            AI agents track redemption periods, statute expirations, and claim windows.
                            90-day cascade alerts prevent missed opportunities.
                        </p>
                    </div>
                </div>
            </section>

            {/* Architecture Section */}
            <section className="py-24 px-6 bg-zinc-900 text-white">
                <div className="max-w-7xl mx-auto">
                    <div className="mb-16">
                        <h2 className="text-3xl font-bold mb-4">Built on Production-Grade Infrastructure</h2>
                        <p className="text-zinc-400 text-lg max-w-2xl">
                            We didn't just wrap a database. We built a specialized operating system
                            tailored for the complexities of distressed assets.
                        </p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        <div className="p-6 rounded-xl bg-zinc-800/50 border border-zinc-700">
                            <Brain className="h-6 w-6 text-indigo-400 mb-4" />
                            <h3 className="text-lg font-bold mb-2">7 Specialized AI Agents</h3>
                            <ul className="text-zinc-400 space-y-2 text-sm">
                                <li>• Calculate interest across 12+ jurisdictions</li>
                                <li>• Monitor court dockets automatically</li>
                                <li>• Generate writs and legal forms</li>
                                <li>• Track redemption deadlines 24/7</li>
                            </ul>
                        </div>

                        <div className="p-6 rounded-xl bg-zinc-800/50 border border-zinc-700">
                            <Database className="h-6 w-6 text-indigo-400 mb-4" />
                            <h3 className="text-lg font-bold mb-2">Polymorphic Data Architecture</h3>
                            <ul className="text-zinc-400 space-y-2 text-sm">
                                <li>• Unified API for all asset types</li>
                                <li>• BaseAsset model with vertical extensions</li>
                                <li>• Dynamic frontend that adapts to asset class</li>
                                <li>• Zero-latency schema migrations</li>
                            </ul>
                        </div>

                        <div className="p-6 rounded-xl bg-zinc-800/50 border border-zinc-700">
                            <ShieldCheck className="h-6 w-6 text-indigo-400 mb-4" />
                            <h3 className="text-lg font-bold mb-2">Enterprise-Ready Deployment</h3>
                            <ul className="text-zinc-400 space-y-2 text-sm">
                                <li>• Google Cloud Run & Firestore NoSQL</li>
                                <li>• Role-based access control (RBAC)</li>
                                <li>• Audit trails and compliance logging</li>
                                <li>• Bank-grade encryption at rest</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </section>

            {/* Supported Verticals */}
            <section className="py-20 px-6 max-w-7xl mx-auto text-center">
                <h2 className="text-sm font-semibold text-zinc-500 uppercase tracking-wider mb-12">
                    Supporting 5 Distressed Asset Classes
                </h2>
                <div className="flex flex-wrap justify-center gap-12 md:gap-20 opacity-80">
                    <div className="flex flex-col items-center gap-3">
                        <FileText className="h-8 w-8 text-zinc-900" />
                        <span className="font-medium text-zinc-700 text-sm">Tax Liens</span>
                    </div>
                    <div className="flex flex-col items-center gap-3">
                        <Gavel className="h-8 w-8 text-zinc-900" />
                        <span className="font-medium text-zinc-700 text-sm">Civil Judgments</span>
                    </div>
                    <div className="flex flex-col items-center gap-3">
                        <Scroll className="h-8 w-8 text-zinc-900" />
                        <span className="font-medium text-zinc-700 text-sm">Probate</span>
                    </div>
                    <div className="flex flex-col items-center gap-3">
                        <Pickaxe className="h-8 w-8 text-zinc-900" />
                        <span className="font-medium text-zinc-700 text-sm">Mineral Rights</span>
                    </div>
                    <div className="flex flex-col items-center gap-3">
                        <Coins className="h-8 w-8 text-zinc-900" />
                        <span className="font-medium text-zinc-700 text-sm">Surplus Funds</span>
                    </div>
                </div>
            </section>

            {/* Social Proof / Traction */}
            <section className="py-16 bg-zinc-50 border-y border-zinc-200">
                <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-3 gap-8 text-center">
                    <div>
                        <div className="text-4xl font-bold text-zinc-900 mb-1">170+</div>
                        <div className="text-zinc-600 font-medium">Assets Under Management</div>
                    </div>
                    <div>
                        <div className="text-4xl font-bold text-zinc-900 mb-1">100%</div>
                        <div className="text-zinc-600 font-medium">Production Ready Code</div>
                    </div>
                    <div>
                        <div className="text-4xl font-bold text-zinc-900 mb-1">MIT</div>
                        <div className="text-zinc-600 font-medium">Open Source License</div>
                    </div>
                </div>
            </section>

            {/* CTA Footer */}
            <section className="py-24 px-6 text-center">
                <h2 className="text-3xl font-bold text-zinc-900 mb-8">
                    Ready to modernize your fund?
                </h2>
                <div className="flex flex-col items-center gap-6">
                    <Link
                        to="/app"
                        className="inline-flex items-center gap-2 bg-indigo-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-indigo-700 transition-colors"
                    >
                        Try the live demo
                        <ArrowRight className="h-5 w-5" />
                    </Link>
                    <p className="text-zinc-500">
                        Questions? Contact: <a href="mailto:sdhines3@gmail.com" className="text-zinc-900 hover:underline">sdhines3@gmail.com</a>
                    </p>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-8 text-center text-sm text-zinc-400 border-t border-zinc-100">
                <p>&copy; {new Date().getFullYear()} AssetOS. Built for Special Situations Investors.</p>
            </footer>
        </div>
    );
};

export default LandingPage;
