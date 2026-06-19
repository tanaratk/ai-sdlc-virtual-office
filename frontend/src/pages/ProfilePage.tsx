import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { User, KeyRound, CheckCircle2, Shield } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { authApi } from "@/services/authApi";
import type { UserRole } from "@/types/auth";

const ROLE_INFO: Record<UserRole, { label: string; color: string; desc: string }> = {
  admin: { label: "Admin", color: "text-red-600 bg-red-100", desc: "Full system access including user management" },
  manager: { label: "Manager", color: "text-blue-600 bg-blue-100", desc: "Can manage projects and approve pipeline steps" },
  user: { label: "User", color: "text-gray-600 bg-gray-100", desc: "Standard access to assigned projects" },
};

export default function ProfilePage() {
  const { user } = useAuth();
  const [name, setName] = useState(user?.name ?? "");
  const [nameSaved, setNameSaved] = useState(false);

  const [currentPw, setCurrentPw] = useState("");
  const [newPw, setNewPw] = useState("");
  const [confirmPw, setConfirmPw] = useState("");
  const [pwError, setPwError] = useState("");
  const [pwSaved, setPwSaved] = useState(false);

  const updateNameMutation = useMutation({
    mutationFn: () => authApi.updateMe({ name: name.trim() }),
    onSuccess: (updatedUser) => {
      localStorage.setItem("auth_user", JSON.stringify(updatedUser));
      // Force re-read by triggering a page-level re-render via storage event
      window.dispatchEvent(new Event("storage"));
      setNameSaved(true);
      setTimeout(() => setNameSaved(false), 2000);
    },
  });

  const changePwMutation = useMutation({
    mutationFn: () =>
      authApi.changePassword({ current_password: currentPw, new_password: newPw }),
    onSuccess: () => {
      setPwSaved(true);
      setCurrentPw("");
      setNewPw("");
      setConfirmPw("");
      setTimeout(() => setPwSaved(false), 2000);
    },
    onError: (err) => setPwError((err as Error).message),
  });

  const handleChangePw = (e: React.FormEvent) => {
    e.preventDefault();
    setPwError("");
    if (newPw !== confirmPw) {
      setPwError("New passwords do not match");
      return;
    }
    changePwMutation.mutate();
  };

  const roleInfo = ROLE_INFO[user?.role ?? "user"];

  return (
    <div className="space-y-6 max-w-lg">
      <h2 className="text-lg font-semibold">Profile</h2>

      {/* Account info */}
      <section className="rounded-lg border bg-white p-5 space-y-4">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-lg font-bold text-primary">
            {user?.name.charAt(0).toUpperCase()}
          </div>
          <div>
            <p className="font-semibold">{user?.name}</p>
            <p className="text-sm text-muted-foreground">{user?.email}</p>
          </div>
          <span className={`ml-auto flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ${roleInfo.color}`}>
            <Shield className="h-3 w-3" />
            {roleInfo.label}
          </span>
        </div>
        <p className="text-xs text-muted-foreground">{roleInfo.desc}</p>
      </section>

      {/* Edit name */}
      <section className="rounded-lg border bg-white p-5 space-y-3">
        <h3 className="flex items-center gap-2 text-sm font-semibold">
          <User className="h-4 w-4" /> Display Name
        </h3>
        <div className="flex gap-2">
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="flex-1 rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
          <button
            onClick={() => updateNameMutation.mutate()}
            disabled={updateNameMutation.isPending || !name.trim() || name.trim() === user?.name}
            className="flex items-center gap-1 rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {nameSaved ? (
              <><CheckCircle2 className="h-3.5 w-3.5" /> Saved!</>
            ) : (
              updateNameMutation.isPending ? "Saving…" : "Save"
            )}
          </button>
        </div>
      </section>

      {/* Change password */}
      <section className="rounded-lg border bg-white p-5 space-y-3">
        <h3 className="flex items-center gap-2 text-sm font-semibold">
          <KeyRound className="h-4 w-4" /> Change Password
        </h3>
        <form onSubmit={handleChangePw} className="space-y-3">
          <div>
            <label className="block text-xs font-medium mb-1">Current Password</label>
            <input
              type="password"
              value={currentPw}
              onChange={(e) => setCurrentPw(e.target.value)}
              required
              className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
          <div>
            <label className="block text-xs font-medium mb-1">New Password</label>
            <input
              type="password"
              value={newPw}
              onChange={(e) => setNewPw(e.target.value)}
              required
              minLength={6}
              className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
          <div>
            <label className="block text-xs font-medium mb-1">Confirm New Password</label>
            <input
              type="password"
              value={confirmPw}
              onChange={(e) => setConfirmPw(e.target.value)}
              required
              className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {pwError && (
            <p className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">{pwError}</p>
          )}

          <button
            type="submit"
            disabled={changePwMutation.isPending}
            className="flex items-center gap-1 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {pwSaved ? (
              <><CheckCircle2 className="h-3.5 w-3.5" /> Changed!</>
            ) : (
              changePwMutation.isPending ? "Changing…" : "Change Password"
            )}
          </button>
        </form>
      </section>
    </div>
  );
}
