export interface PlaylistContentItem {
  item: {
    playlistid: string;
    filmid: string;
    creatorid: string;
  };
  preview: {
    filmid: string;
    season: number;
    is_series: boolean;
    seasons_info: {
      number: number;
      episodes_count: number;
    }[];
    already_added: boolean;
    is_watched: boolean;
    user_rating: {
      storyline: number;
      music: number;
      montage: number;
      acting_game: number;
      atmosphere: number;
      originality: number;
    };
    last_updated: string;
    added_at: string;
    playlists: string[];
    name: string;
    poster_link: string;
    release_year: number;
    alternative_name: string;
    genres: string[];
    countries: string[];
    director: string;
    time_minutes: number;
    age_rating: number;
  };
}

export type PlaylistContentResponse = PlaylistContentItem[];
