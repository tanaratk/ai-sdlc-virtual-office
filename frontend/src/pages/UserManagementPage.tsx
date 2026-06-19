import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Shield, Users, UserX, UserCheck, Trash2 } from "lucide-react";
import { authApi } from "@/services/authApi";
import { useAuth } from "@/context/AuthContext";
import type { UserRole } from "@/types/auth";

const ROLE_COLORS: Record<UserRole, string> = {
  admin: "bg-red-100 text-red-700",
  manager: "bg-blue-100 text-blue-700",
  user: "bg-gray-100 text-gray-700",
};

export default function UserManagementPage() {
  const { user: me } = useAuth();
  const queryClient = useQueryClient();
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);

  const { data: users = [], isLoading } = useQuery({
    queryKey: ["users"],
    queryFn: authApi.listUsers,
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof authApi.updateUser>[1] }) =>
      authApi.updateUser(id, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => authApi.deleteUser(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      setConfirmDelete(null);
    },
  });

  return (
    <div className="space-y-4 max-w-4xl">
      <div className="flex items-center gap-2">
        <Users className="h-5 w-5 text-primary" />
        <h2 className="text-lg font-semibold">User Management</h2>
        <span className="ml-auto text-sm text-muted-foreground">{users.length} users</span>
      </div>

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading users…</p>
      ) : (
        <div className="rounded-lg border bg-white overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/30 text-xs text-muted-foreground">
                <th className="px-4 py-3 text-left font-medium">Name</th>
                <th className="px-4 py-3 text-left font-medium">Email</th>
                <th className="px-4 py-3 text-left font-medium">Role</th>
                <th className="px-4 py-3 text-left font-medium">Status</th>
                <th className="px-4 py-3 text-left font-medium">Joined</th>
                <th className="px-4 py-3 text-left font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {users.map((u) => {
                const isMe = u.id === me?.id;
                return (
                  <tr key={u.id} className={`hover:bg-muted/20 ${!u.is_active ? "opacity-50" : ""}`}>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary/10 text-xs font-medium text-primary">
                          {u.name.charAt(0).toUpperCase()}
                        </div>
                        <span className="font-medium">
                          {u.name}
                          {isMe && <span className="ml-1 text-xs text-muted-foreground">(you)</span>}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">{u.email}</td>
                    <td className="px-4 py-3">
                      <select
                        value={u.role}
                        disabled={isMe || updateMutation.isPending}
                        onChange={(e) =>
                          updateMutation.mutate({ id: u.id, data: { role: e.target.value as UserRole } })
                        }
                        className={`rounded-full px-2 py-0.5 text-xs font-medium border-0 cursor-pointer disabled:cursor-not-allowed ${ROLE_COLORS[u.role as UserRole]}`}
                      >
                        <option value="user">User</option>
                        <option value="manager">Manager</option>
                        <option value="admin">Admin</option>
                      </select>
                    </td>
                    <td className="px-4 py-3">
                      <button
                        disabled={isMe || updateMutation.isPending}
                        onClick={() =>
                          updateMutation.mutate({ id: u.id, data: { is_active: !u.is_active } })
                        }
                        className={`flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium disabled:cursor-not-allowed ${
                          u.is_active
                            ? "bg-green-100 text-green-700 hover:bg-green-200"
                            : "bg-gray-100 text-gray-500 hover:bg-gray-200"
                        }`}
                      >
                        {u.is_active ? (
                          <><UserCheck className="h-3 w-3" /> Active</>
                        ) : (
                          <><UserX className="h-3 w-3" /> Disabled</>
                        )}
                      </button>
                    </td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      {!isMe && (
                        confirmDelete === u.id ? (
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => deleteMutation.mutate(u.id)}
                              disabled={deleteMutation.isPending}
                              className="text-xs text-destructive hover:underline"
                            >
                              {deleteMutation.isPending ? "Deleting…" : "Confirm"}
                            </button>
                            <button
                              onClick={() => setConfirmDelete(null)}
                              className="text-xs text-muted-foreground hover:underline"
                            >
                              Cancel
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={() => setConfirmDelete(u.id)}
                            className="text-muted-foreground hover:text-destructive"
                            aria-label="Delete user"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        )
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <div className="rounded-lg border bg-muted/20 p-4 text-xs text-muted-foreground space-y-1">
        <p className="flex items-center gap-1"><Shield className="h-3 w-3 text-red-500" /> <strong>Admin</strong> — full access: user management, all projects, all settings</p>
        <p className="flex items-center gap-1"><Shield className="h-3 w-3 text-blue-500" /> <strong>Manager</strong> — can create/manage projects, approve pipeline steps</p>
        <p className="flex items-center gap-1"><Shield className="h-3 w-3 text-gray-400" /> <strong>User</strong> — read access, can contribute to assigned projects</p>
      </div>
    </div>
  );
}
