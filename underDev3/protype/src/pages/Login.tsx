// ...existing code...
import { Input } from "../../ui/innput";
import { Button } from "../../ui/button";
import { Checkbox } from "../../ui/checkbox";
import { Select, SelectItem } from "../../ui/select";
// replace the named import with an alias
import { useState as useReactState } from "react";
// ...existing code...
export default function Login() {
  const [agreed, setAgreed] = useReactState(false);
  const [country, setCountry] = useReactState("");
// ...existing code...

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

function useState(arg0: string): [any, any] {
  throw new Error("Function not implemented.");
}
