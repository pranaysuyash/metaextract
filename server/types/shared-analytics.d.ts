declare module '@shared/analytics-events' {
  export const EventName: any;
  export const UserIntentEvent: any;
  export const ComprehensionEvent: any;
  export type BaseEventProperties = Record<string, unknown>;
  export type UserIntentEventProperties = Record<string, unknown>;
  export type ComprehensionEventProperties = Record<string, unknown>;
  export function buildDedupeKey(...args: any[]): string;
  export function validateEventPayload(payload: any): any;
  export enum FileSizeBucket { SMALL = 'SMALL', MEDIUM = 'MEDIUM', LARGE = 'LARGE', XLARGE = 'XLARGE' }
  export enum UserTier { ANON = 'ANON', FREE = 'FREE', PRO = 'PRO' }
  export enum AuthState { LOGGED_OUT = 'LOGGED_OUT', LOGGED_IN = 'LOGGED_IN' }
  export enum SourceEntryPoint { UPLOAD_PAGE = 'UPLOAD_PAGE', LANDING = 'LANDING', SHARE_LINK = 'SHARE_LINK', API = 'API' }
  export enum ClientType { WEB = 'WEB', EXTENSION = 'EXTENSION', MOBILE_APP = 'MOBILE_APP' }
  export enum ResultDensity { SIMPLE = 'SIMPLE', STANDARD = 'STANDARD', ADVANCED = 'ADVANCED' }
  export const validateEvent: any;
  export type InsertUiEvent = any;
}
