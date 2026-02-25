import { useState } from "react";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { Checkbox } from "../components/ui/checkbox";
import { Select, SelectItem } from "../components/ui/select";

export default function Login() {
  const [agreed, setAgreed] = useState(false);
  const [country, setCountry] = useState("");

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center px-6">
      <div className="w-full max-w-md space-y-6">
        <h1 className="text-4xl font-bold text-[#1f3b63] text-center">Login</h1>

        <div className="text-center space-y-1">
          <p className="font-semibold text-sm">Sign in to access the CT analysis.</p>
          <p className="text-slate-600 text-xs">Please use your authorised account to access the platform.</p>
          <p className="text-slate-500 text-xs">
            By logging in, you agree to handle all uploaded data in accordance with applicable privacy and data protection requirements.
          </p>
        </div>

        <div className="space-y-4">
          <Input placeholder="Email" type="email" />
          <Input placeholder="Password" type="password" />

          <Select value={country} onValueChange={setCountry}>
            <option value="" disabled>
              Country
            </option>
            <SelectItem value="no">Norway</SelectItem>
            <SelectItem value="se">Sweden</SelectItem>
            <SelectItem value="dk">Denmark</SelectItem>
            <SelectItem value="fi">Finland</SelectItem>
            <SelectItem value="uk">United Kingdom</SelectItem>
            <SelectItem value="us">United States</SelectItem>
            <SelectItem value="de">Germany</SelectItem>
            <SelectItem value="other">Other</SelectItem>
          </Select>

          <div className="flex items-center gap-2">
            <Checkbox id="terms" checked={agreed} onCheckedChange={setAgreed} />
            <label htmlFor="terms" className="text-xs">
              By clicking you agree to the{" "}
              <span className="text-slate-600 font-semibold cursor-pointer">Terms and Conditions</span>
            </label>
          </div>

          <Button className="w-full py-3 text-sm" disabled={!agreed}>
            SIGN IN
          </Button>

          <p className="text-center text-sm">
            No account? <span className="text-slate-600 font-semibold cursor-pointer">Create one</span>
          </p>
        </div>
      </div>
    </div>
  );
}