// Human messages for API error codes (api/app/errors.py). Unknown codes fall back
// to the server message.
const MESSAGES: Record<string, string> = {
  INVALID_CREDENTIALS: "Wrong email or password.",
  USER_INACTIVE: "This account has been deactivated.",
  NOT_AUTHENTICATED: "Please log in first.",
  INVALID_TOKEN: "Your session expired. Please log in again.",
  EMAIL_TAKEN: "An account with this email already exists.",
  WRONG_PASSWORD: "Your current password is incorrect.",
  FORBIDDEN_ROLE: "You don't have permission to do that.",
  NOT_ADMIN: "Only administrators can do that.",
  DB_PERMISSION_DENIED: "The database refused this operation.",
  SKILL_EXISTS: "That skill already exists in the catalogue.",
  SKILL_NOT_ON_PROFILE: "That skill isn't on your profile.",
  INVALID_REFERENCE: "That item no longer exists.",
  LAST_ADMIN: "There must always be at least one active admin.",
  OWNS_ONGOING_PROJECTS: "Transfer or finish your ongoing projects first.",
  CHECK_VIOLATION: "Some values are out of range (e.g. a deadline before the project was created).",
  NOT_OWNER: "Only the project owner can do that.",
  PROJECT_NOT_FOUND: "That project doesn't exist.",
  PROJECT_REOPEN_FORBIDDEN: "Completed or closed projects can't be reopened.",
  REQUIREMENT_NOT_FOUND: "That requirement was already removed.",
  SAME_PROJECT: "Pick a different project to copy from.",
  PROJECT_NOT_OPEN: "This project isn't accepting applications.",
  PROJECT_FULL: "The team is already full.",
  SELF_APPLICATION: "You can't apply to your own project.",
  DUPLICATE_PENDING: "You already have a pending application for this project.",
  ALREADY_MEMBER: "That person is already on the team.",
  APP_NOT_PENDING: "This application has already been decided or withdrawn.",
  NOT_APPLICANT: "Only the applicant can withdraw this application.",
  PROJECT_NOT_ACCEPTING: "Members can only be added while the project is Open or Ongoing.",
  PROJECT_FINISHED: "Completed or closed projects can't get new tasks.",
  CAPACITY_BELOW_TEAM: "The team already has more members than that limit.",
  DEADLINE_BEFORE_TASKS: "Some unfinished tasks are due after that deadline. Move them first.",
  PARENT_OTHER_PROJECT: "A subtask must belong to the same project as its parent.",
  NOT_ACTIVE_MEMBER: "That person isn't an active member of this team.",
  OWNER_CANNOT_LEAVE: "Transfer ownership before leaving the team.",
  NOT_MEMBER: "Only team members can do that.",
  APP_NOT_FOUND: "That application doesn't exist.",
  TASK_NOT_FOUND: "That task doesn't exist.",
  USER_NOT_FOUND: "That user doesn't exist.",
  SKILL_NOT_FOUND: "That skill doesn't exist.",
  ASSIGNEE_NOT_MEMBER: "Tasks can only be assigned to active team members.",
  TASK_AFTER_DEADLINE: "A task can't be due after the project deadline.",
  BAD_DECISION: "Choose Accept or Reject.",
  BAD_ROLE: "That role isn't allowed.",
  TEAM_EXISTS: "This project already has a team.",
  ALREADY_EXISTS: "That already exists.",
  DUPLICATE: "That already exists.",
  IN_USE: "That item is still in use and can't be removed.",
  MISSING_VALUE: "A required value is missing.",
  SELF_ENDORSEMENT: "You can't endorse yourself.",
  NOT_COLLABORATORS: "You can only endorse people you've shared a team with.",
  ENDORSEMENT_NOT_FOUND: "That endorsement was already removed.",
  SAME_SKILL: "A skill can't be related to itself.",
  RELATION_NOT_FOUND: "Those skills aren't related.",
  UNKNOWN_FORM: "That form doesn't exist.",
  GRAPH_UNAVAILABLE: "Graph features are temporarily unavailable. Everything else still works.",
  DEV_ONLY: "This action is only available in development.",
  RETRY: "The database was busy. Please try again.",
  API_UNAVAILABLE: "The server is unreachable. Please try again shortly.",
  VALIDATION: "Please check the highlighted fields.",
};

export interface ApiErrorBody {
  code?: string;
  message?: string;
  detail?: unknown;
}

export function messageFor(body: ApiErrorBody | null | undefined): string {
  if (!body) return "Something went wrong. Please try again.";
  if (body.detail) return MESSAGES.VALIDATION;            // FastAPI request validation (422)
  return (body.code && MESSAGES[body.code]) || body.message || "Something went wrong.";
}
