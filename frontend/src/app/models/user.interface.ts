export interface UserShort {
    userid: string;
    role: number;
    status: number;
  }
  
  export interface UserProfile extends UserShort {
    username: string;
    bio: string;
    location: string;
    birth_date: string;
    email: string;
    avatar: string;
  }
  
  export interface Subscriber {
    userid: string;
    role: number;
    status: number;
    username: string;
    subscribers_count: number;
    avatar: string;
  }

  export interface UpdateUserProfileRequest {
    userid: string;
    username: string | null;
    bio: string | null;
    location: string | null;
    birth_date: string | null;
    email: string | null;
    avatar: string | null;
    status: number;
  }