import React, { useState, useEffect } from "react";
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import FileUpload from './FileUpload';

export default function DashboardMockup() {
  const { user, logout } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showFileUpload, setShowFileUpload] = useState(false);

  // Load initial data
  useEffect(() => {
    const loadData = async () => {
      try {
        const [transactionsData, categoriesData] = await Promise.all([
          api.transactions.getTransactions({ limit: 4 }),
          api.categories.getCategories(),
        ]);
        
        setTransactions(transactionsData || []);
        setCategories(categoriesData || []);
      } catch (err) {
        setError('Failed to load data');
        console.error('Error loading data:', err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Handle successful file upload
  const handleUploadSuccess = async (result) => {
    console.log('Upload successful:', result);
    // Reload transactions to show newly imported data
    try {
      const transactionsData = await api.transactions.getTransactions({ limit: 4 });
      setTransactions(transactionsData || []);
    } catch (err) {
      console.error('Error reloading transactions:', err);
    }
  };
  return (
    <div className="min-h-screen bg-slate-50 p-8 font-sans">
      <div className="max-w-7xl mx-auto">
        <header className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-semibold">Shared Finance — Dashboard</h1>
            <p className="text-sm text-slate-500">Welcome back, {user?.user_email || user?.email || 'User'}</p>
          </div>
          <div className="flex items-center gap-3">
            <button className="px-4 py-2 bg-white border rounded-lg text-sm">Settings</button>
            <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm">Invite Partner</button>
            <button 
              onClick={logout}
              className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700"
            >
              Logout
            </button>
            <img src="https://avatars.dicebear.com/api/micah/user.svg" alt="avatar" className="w-10 h-10 rounded-full" />
          </div>
        </header>

        <section className="grid grid-cols-12 gap-6 mb-6">
          <div className="col-span-7 bg-white p-6 rounded-2xl shadow-sm">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-lg font-medium">This month overview</h2>
                <p className="text-sm text-slate-500">Aug 2025 • Combined</p>
              </div>
              <div className="text-right">
                <div className="text-sm text-slate-400">Remaining Balance</div>
                <div className="text-2xl font-bold">$2,730.50</div>
                <div className="text-sm text-slate-500">Income: $8,200 • Expenses: $5,469.50</div>
              </div>
            </div>

            <div className="mt-6 grid grid-cols-3 gap-4">
              <StatCard title="You (Satya)" amount="$4,800" subtitle="Net after expenses: $1,220" />
              <StatCard title="Partner" amount="$3,400" subtitle="Net after expenses: $1,510" />
              <StatCard title="Combined Savings" amount="$2,730.50" subtitle="Carry-forward: $300" />
            </div>

            <div className="mt-6">
              <h3 className="text-sm text-slate-600 mb-2">Income vs Expenses (3 months)</h3>
              <PlaceholderLineChart />
            </div>
          </div>

          <aside className="col-span-5 space-y-4">
            <div className="bg-white p-4 rounded-2xl shadow-sm">
              <h3 className="text-sm font-medium mb-2">Quick Actions</h3>
              <div className="flex gap-2">
                <button 
                  onClick={() => setShowFileUpload(true)}
                  className="px-3 py-2 border rounded-lg text-sm hover:bg-indigo-50 hover:border-indigo-300"
                >
                  Upload PDF
                </button>
                <button className="px-3 py-2 border rounded-lg text-sm">Add Income</button>
                <button className="px-3 py-2 border rounded-lg text-sm">New Goal</button>
              </div>
              <p className="mt-3 text-xs text-slate-500">Tip: Upload bank PDF statements to auto‑parse transactions.</p>
            </div>

            <div className="bg-white p-4 rounded-2xl shadow-sm">
              <h3 className="text-sm font-medium">Investment Goals</h3>
              <GoalRow name="Home Downpayment" progress={30} target="$50,000" eta="May 2027" />
              <GoalRow name="Emergency Fund" progress={65} target="$9,000" eta="Dec 2025" />
            </div>

            <div className="bg-white p-4 rounded-2xl shadow-sm">
              <h3 className="text-sm font-medium">Alerts & Insights</h3>
              <ul className="mt-2 text-sm text-slate-600 space-y-2">
                <li>Dining out +24% vs last month — consider a weekly meal plan.</li>
                <li>Unrecognized subscription: StreamingX — $12/mo.</li>
                <li>Suggested extra to reach Home Downpayment 3 months earlier: $450/mo.</li>
              </ul>
            </div>
          </aside>
        </section>

        <section className="grid grid-cols-12 gap-6">
          <div className="col-span-4 bg-white p-4 rounded-2xl shadow-sm">
            <h3 className="text-sm font-medium mb-4">Top Categories</h3>
            <CategoryRow name="Groceries" amount="$720" percent={18} />
            <CategoryRow name="Rent" amount="$1,600" percent={40} />
            <CategoryRow name="Dining Out" amount="$420" percent={10} />
            <CategoryRow name="Transport" amount="$180" percent={5} />
          </div>

          <div className="col-span-8 bg-white p-4 rounded-2xl shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium">Recent Transactions</h3>
              <div className="text-sm text-slate-500">Showing combined</div>
            </div>

            <table className="w-full text-sm">
              <thead className="text-left text-slate-500 text-xs">
                <tr>
                  <th className="pb-2">Date</th>
                  <th className="pb-2">Description</th>
                  <th className="pb-2">Category</th>
                  <th className="pb-2 text-right">Amount</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan="4" className="py-8 text-center text-slate-500">
                      Loading transactions...
                    </td>
                  </tr>
                ) : transactions.length > 0 ? (
                  transactions.map((transaction) => (
                    <TransactionRow
                      key={transaction.id}
                      date={new Date(transaction.date).toLocaleDateString()}
                      desc={transaction.description}
                      cat={transaction.category_name || "Uncategorized"}
                      amt={transaction.amount.toFixed(2)}
                      who="You"
                    />
                  ))
                ) : (
                  <tr>
                    <td colSpan="4" className="py-8 text-center text-slate-500">
                      No transactions found. Try uploading a bank statement!
                    </td>
                  </tr>
                )}
              </tbody>
            </table>

            <div className="mt-4 text-right">
              <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm">View full history</button>
            </div>
          </div>
        </section>

        {/* File Upload Modal */}
        {showFileUpload && (
          <FileUpload
            onUploadSuccess={handleUploadSuccess}
            onClose={() => setShowFileUpload(false)}
          />
        )}

      </div>
    </div>
  );
}

function StatCard({ title, amount, subtitle }) {
  return (
    <div className="p-4 bg-slate-50 rounded-xl border">
      <div className="text-xs text-slate-500">{title}</div>
      <div className="text-lg font-semibold">{amount}</div>
      <div className="text-xs text-slate-400 mt-1">{subtitle}</div>
    </div>
  );
}

function PlaceholderLineChart() {
  return (
    <div className="w-full h-40 bg-gradient-to-r from-white to-slate-50 rounded-lg border flex items-center justify-center">
      <svg width="100%" height="120" viewBox="0 0 400 120" xmlns="http://www.w3.org/2000/svg">
        <polyline fill="none" stroke="#6366f1" strokeWidth="3" points="0,90 40,70 80,60 120,75 160,50 200,40 240,55 280,30 320,45 360,20 400,30" />
      </svg>
    </div>
  );
}

function GoalRow({ name, progress, target, eta }) {
  return (
    <div className="mt-3">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm font-medium">{name}</div>
          <div className="text-xs text-slate-500">Target: {target} • ETA: {eta}</div>
        </div>
        <div className="text-sm font-semibold">{progress}%</div>
      </div>
      <div className="w-full bg-slate-100 h-2 rounded-full mt-2 overflow-hidden">
        <div style={{ width: `${progress}%` }} className="h-2 rounded-full bg-emerald-400" />
      </div>
    </div>
  );
}

function CategoryRow({ name, amount, percent }) {
  return (
    <div className="flex items-center justify-between py-3 border-b last:border-b-0">
      <div>
        <div className="text-sm font-medium">{name}</div>
        <div className="text-xs text-slate-500">{percent}% of spending</div>
      </div>
      <div className="text-sm font-semibold">{amount}</div>
    </div>
  );
}

function TransactionRow({ date, desc, cat, amt, who }) {
  return (
    <tr className="border-t">
      <td className="py-3 text-slate-600">{date}</td>
      <td className="py-3">{desc} <div className="text-xs text-slate-400">{who}</div></td>
      <td className="py-3 text-slate-600">{cat}</td>
      <td className="py-3 text-right font-medium">{amt}</td>
    </tr>
  );
}
