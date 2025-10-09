export interface Playlist {
    userid: string;
    playlistid: string;
    name: string;
    description: string;
    is_public: boolean;
    additions_count: boolean;
    gen_attrs: GenAttrs;
    collaborators: any[];
  }
  
  export interface GenAttrs {
    filmid: string;
    name: string;
    person: string;
    is_series: boolean;
    year: RangeNumber;
    kp_rating: RangeNumber;
    length: RangeNumber;
    age_rating: RangeNumber;
    genres: string[];
    countries: string[];
    is_watched: boolean;
    user_rating: UserRating;
  }
  
  export interface RangeNumber {
    lower: number;
    upper: number;
  }
  
  export interface UserRating {
    storyline: number;
    music: number;
    montage: number;
    acting_game: number;
    atmosphere: number;
    originality: number;
  }