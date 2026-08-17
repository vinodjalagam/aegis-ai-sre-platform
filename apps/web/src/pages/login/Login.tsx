import { useState } from "react";
import { ShieldCheck } from "lucide-react";
import { login } from "../../api/auth";
import "./Login.css";

interface LoginProps {
  onLogin: () => void;
}

function Login({ onLogin }: LoginProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(
    event: Parameters<NonNullable<React.ComponentProps<"form">["onSubmit"]>>[0]
  ) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      await login({
        username,
        password,
      });

      onLogin();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Invalid username or password"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        {/* Brand */}
        <div className="login-brand">
          <div className="login-mark">
            <ShieldCheck size={28} />
          </div>

          <div>
            <strong>AEGIS</strong>
            <span>AI SRE PLATFORM</span>
          </div>
        </div>

        {/* Heading */}
        <div className="login-heading">
          <p className="eyebrow">SECURE ACCESS</p>

          <h1>Welcome back</h1>

          <p>
            Sign in to access the Aegis SRE operations platform.
          </p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit}>
          <label>
            Username

            <input
              type="text"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              placeholder="Enter username"
              autoComplete="username"
              required
              disabled={loading}
            />
          </label>

          <label>
            Password

            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter password"
              autoComplete="current-password"
              required
              disabled={loading}
            />
          </label>

          {/* Error */}
          {error && (
            <div className="login-error">
              {error}
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        {/* Footer */}
        <div className="login-footer">
          <span>AEGIS AI SRE</span>
          <span>Secure Operations</span>
        </div>
      </div>
    </div>
  );
}

export default Login;