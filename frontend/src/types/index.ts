// Domain types mirroring the backend API responses.

export interface Player {
  player_id: number;
  first_name: string;
  last_name: string;
  birthdate: string;
  birth_country: string | null;
  birth_state: string | null;
  height_feet: number;
  height_inches: number;
  weight: number;
  team: string;
  primary_position: string;
  throws: string;
  bats: string;
}

export interface Pitch {
  rowid: number;
  pitch_type: string | null;
  pitch_name: string | null;
  game_date: string;
  player_name: string | null;
  pitcher: number;
  batter: number;
  release_speed: number | null;
  release_spin_rate: number | null;
  plate_x: number | null;
  plate_z: number | null;
  zone: number | null;
  type: string | null;
  description: string | null;
  events: string | null;
  balls: number | null;
  strikes: number | null;
  outs_when_up: number | null;
  inning: number | null;
  inning_topbot: string | null;
  launch_speed: number | null;
  launch_angle: number | null;
  hit_distance_sc: number | null;
  stand: string | null;
  p_throws: string | null;
  home_team: string | null;
  away_team: string | null;
}

export interface Pagination {
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
}

export interface Paginated<T> {
  data: T[];
  pagination: Pagination;
}

export interface PlayerFilterOptions {
  team?: string;
  position?: string;
  search?: string;
  page?: number;
  per_page?: number;
}

export interface PitchFilterOptions {
  pitcher?: number;
  batter?: number;
  player_id?: number;
  pitch_type?: string;
  team?: string;
  min_velocity?: number;
  max_velocity?: number;
  start_date?: string;
  end_date?: string;
  page?: number;
  per_page?: number;
}

export interface PitchType {
  code: string;
  name: string;
}
