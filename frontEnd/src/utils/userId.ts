/**
 * Generates a UserID from name + personnummer.
 *
 * Format: [2 chars first name][2 chars last name][2-digit birth day][2-digit counter]
 * Example: Younes Benhaid, personnummer 2808031XXXX → yobe2801
 *
 * Counter starts at 01 and only increments if the prefix already exists.
 */
export function generateUserId(
  firstName: string,
  lastName: string,
  personnummer: string,
  existingIds: string[]
): string {
  const fn = firstName
    .toLowerCase()
    .replace(/[^a-z]/g, "")
    .slice(0, 2)
    .padEnd(2, "x");

  const ln = lastName
    .toLowerCase()
    .replace(/[^a-z]/g, "")
    .slice(0, 2)
    .padEnd(2, "x");

  // Norwegian personnummer: DDMMYY + 5 digits — day is first 2 chars
  const day = personnummer.replace(/\s/g, "").slice(0, 2);

  const prefix = fn + ln + day;

  for (let counter = 1; counter <= 99; counter++) {
    const id = `${prefix}${String(counter).padStart(2, "0")}`;
    if (!existingIds.includes(id)) return id;
  }

  throw new Error(`No available user IDs for prefix "${prefix}" (all 01–99 taken).`);
}

/**
 * Generates a random 10-character temporary password.
 * Excludes ambiguous characters (0/O, 1/l/I).
 */
export function generateTempPassword(): string {
  const chars =
    "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789@#!";
  return Array.from(
    { length: 10 },
    () => chars[Math.floor(Math.random() * chars.length)]
  ).join("");
}
