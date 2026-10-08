"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { api } from "@/lib/api";
import ProtectedRoute from "@/components/ProtectedRoute";
import Navbar from "@/components/Navbar";
import { motion } from "framer-motion";
import toast, { Toaster } from "react-hot-toast";
import { 
  User, Shield, Key, Building, Mail, CheckCircle2, 
  Lock, Save, ArrowLeft, Cpu, Database 
} from "lucide-react";
import Link from "next/link";

export default function SettingsPage() {
  const { user } = useAuth();
  
  // Profile edit state
  const [fullName, setFullName] = useState("");
  const [orgName, setOrgName] = useState("");
  const [savingProfile, setSavingProfile] = useState(false);

  // Password change state
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [savingPassword, setSavingPassword] = useState(false);

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || "");
      setOrgName(user.org_name || "");
    }
  }, [user]);

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setSavingProfile(true);
    try {
      await api.updateProfile(fullName, orgName);
      toast.success("Profile updated successfully!");
    } catch (err) {
      toast.error(err.message || "Failed to update profile");
    } finally {
      setSavingProfile(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    if (newPassword.length < 6) {
      toast.error("New password must be at least 6 characters");
      return;
    }
    if (newPassword !== confirmPassword) {
      toast.error("New passwords do not match");
      return;
    }
    setSavingPassword(true);
    try {
      await api.changePassword(newPassword, currentPassword);
      toast.success("Password changed successfully!");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err) {
      toast.error(err.message || "Failed to change password");
    } finally {
      setSavingPassword(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-midnight text-slate-100 flex flex-col">
        <Navbar />
        <Toaster position="top-right" />

        <div className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <Link 
                href="/dashboard" 
                className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-cyber-cyan mb-2 transition-colors"
              >
                <ArrowLeft size={16} /> Back to Documents
              </Link>
              <h1 className="text-3xl font-bold text-white tracking-wide">Account & Security Settings</h1>
              <p className="text-sm text-slate-400 mt-1">Manage your team profile, security credentials, and platform preferences.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            {/* Left Column: Profile Card */}
            <div className="space-y-6">
              <div className="glass-panel p-6 rounded-2xl border border-white/5 bg-midnight/60">
                <div className="flex flex-col items-center text-center">
                  <div className="w-20 h-20 rounded-full bg-cyber-cyan/10 border border-cyber-cyan/30 flex items-center justify-center text-cyber-cyan mb-4">
                    <User size={36} />
                  </div>
                  <h3 className="text-lg font-bold text-white">{user?.full_name || "User"}</h3>
                  <p className="text-xs text-slate-400 mt-0.5">{user?.email}</p>
                  
                  <div className="mt-3 flex items-center gap-2">
                    <span className="px-3 py-1 rounded-full text-xs font-semibold tracking-wider bg-cyber-cyan/20 text-cyber-cyan border border-cyber-cyan/30 uppercase">
                      {user?.role || "ANALYST"}
                    </span>
                  </div>

                  <div className="w-full mt-6 pt-6 border-t border-white/5 text-left space-y-3 text-xs">
                    <div className="flex justify-between text-slate-400">
                      <span>Organization:</span>
                      <span className="text-white font-medium">{user?.org_name || "DSATM"}</span>
                    </div>
                    <div className="flex justify-between text-slate-400">
                      <span>Status:</span>
                      <span className="text-cyber-green font-medium flex items-center gap-1">
                        <CheckCircle2 size={12} /> Active
                      </span>
                    </div>
                    <div className="flex justify-between text-slate-400">
                      <span>Engine Access:</span>
                      <span className="text-cyber-cyan font-mono">Gemini / GPT-4o / Claude</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Architecture Info Card */}
              <div className="glass-panel p-5 rounded-2xl border border-white/5 bg-midnight/40 text-xs text-slate-400 space-y-2">
                <div className="flex items-center gap-2 text-white font-semibold">
                  <Cpu size={16} className="text-cyber-cyan" /> Multi-Model Architecture
                </div>
                <p>JURY-AI is powered by 4 interconnected LLM providers with automatic fallback and local ChromaDB persistence.</p>
              </div>
            </div>

            {/* Right Column: Edit Profile & Change Password */}
            <div className="lg:col-span-2 space-y-8">
              
              {/* Profile Details Section */}
              <div className="glass-panel p-6 rounded-2xl border border-white/5 bg-midnight/60">
                <div className="flex items-center gap-2.5 mb-6 pb-4 border-b border-white/5">
                  <Building className="text-cyber-cyan" size={20} />
                  <h2 className="text-lg font-semibold text-white">Profile & Organization Details</h2>
                </div>

                <form onSubmit={handleUpdateProfile} className="space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1.5">Full Name</label>
                    <input
                      type="text"
                      required
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="w-full bg-midnight-light border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyber-cyan transition-colors"
                      placeholder="Your full name"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1.5">Organization / Department</label>
                    <input
                      type="text"
                      required
                      value={orgName}
                      onChange={(e) => setOrgName(e.target.value)}
                      className="w-full bg-midnight-light border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyber-cyan transition-colors"
                      placeholder="e.g. DSATM CSE"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1.5">Email Address (Read-only)</label>
                    <input
                      type="email"
                      disabled
                      value={user?.email || ""}
                      className="w-full bg-black/40 border border-white/5 rounded-lg px-4 py-2.5 text-sm text-slate-500 cursor-not-allowed font-mono"
                    />
                  </div>

                  <div className="pt-2">
                    <button
                      type="submit"
                      disabled={savingProfile}
                      className="bg-cyber-cyan text-midnight-dark font-semibold px-5 py-2.5 rounded-lg text-sm hover:shadow-glow-cyan transition-all flex items-center gap-2 disabled:opacity-50"
                    >
                      <Save size={16} />
                      {savingProfile ? "Saving Changes..." : "Save Profile Details"}
                    </button>
                  </div>
                </form>
              </div>

              {/* Change Password Section */}
              <div className="glass-panel p-6 rounded-2xl border border-white/5 bg-midnight/60">
                <div className="flex items-center gap-2.5 mb-6 pb-4 border-b border-white/5">
                  <Key className="text-cyber-yellow" size={20} />
                  <h2 className="text-lg font-semibold text-white">Security & Change Password</h2>
                </div>

                <form onSubmit={handleChangePassword} className="space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1.5">Current Password</label>
                    <input
                      type="password"
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                      placeholder="Enter current password (or leave blank if using demo credentials)"
                      className="w-full bg-midnight-light border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyber-cyan transition-colors"
                    />
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-slate-300 mb-1.5">New Password</label>
                      <input
                        type="password"
                        required
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        placeholder="At least 6 characters"
                        className="w-full bg-midnight-light border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyber-cyan transition-colors"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-300 mb-1.5">Confirm New Password</label>
                      <input
                        type="password"
                        required
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="Confirm password"
                        className="w-full bg-midnight-light border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyber-cyan transition-colors"
                      />
                    </div>
                  </div>

                  <div className="pt-2">
                    <button
                      type="submit"
                      disabled={savingPassword}
                      className="bg-cyber-yellow text-midnight-dark font-semibold px-5 py-2.5 rounded-lg text-sm hover:shadow-[0_0_15px_rgba(251,191,36,0.3)] transition-all flex items-center gap-2 disabled:opacity-50"
                    >
                      <Lock size={16} />
                      {savingPassword ? "Updating Password..." : "Update Password"}
                    </button>
                  </div>
                </form>
              </div>

            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
