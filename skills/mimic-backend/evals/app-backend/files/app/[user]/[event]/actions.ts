"use server";
import { db } from "@/lib/db";

export async function createBooking(input: {
  hostId: string; eventTypeId: string; startAt: string; endAt: string;
  guestName: string; guestEmail: string; guestTimeZone: string;
}) {
  const { data, error } = await db.from("bookings").insert({
    host_id: input.hostId, event_type_id: input.eventTypeId,
    start_at: input.startAt, end_at: input.endAt,
    guest_name: input.guestName, guest_email: input.guestEmail,
    guest_time_zone: input.guestTimeZone, status: "confirmed",
  }).select().single();
  if (error?.code === "23505") return { ok: false, reason: "slot_taken" };
  if (error) throw error;
  return { ok: true, booking: data };
}
