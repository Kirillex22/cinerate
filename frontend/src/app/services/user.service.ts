import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { UserProfile, UserShort, Subscriber, UpdateUserProfileRequest } from '../models/user.interface';
import { BASE_URL } from '../models/config';


@Injectable({
  providedIn: 'root'
})
export class UserService {
  private baseUrl = BASE_URL;

  constructor(private http: HttpClient) {}

  getCurrentUser(): Observable<UserShort> {
    return this.http.get<UserShort>(`${this.baseUrl}users/current`, {
      withCredentials: true
    });
  }

  getUserById(id: string): Observable<UserProfile> {
    return this.http.get<UserProfile>(`${this.baseUrl}users/${id}`, {
      withCredentials: true
    });
  }

  getSubscribers(id: string): Observable<Subscriber[]> {
    return this.http.get<Subscriber[]>(`${this.baseUrl}users/${id}/subscribers`, {
      withCredentials: true
    });
  }

  getSubscriptions(id: string): Observable<Subscriber[]> {
    return this.http.get<Subscriber[]>(`${this.baseUrl}users/${id}/subscribes`, {
      withCredentials: true
    });
  }

  subscribe(id: string) {
    return this.http.post(`${this.baseUrl}users/${id}/subscribe`, {}, {
      withCredentials: true
    });
  }

  unsubscribe(id: string) {
    return this.http.post(`${this.baseUrl}users/${id}/unsubscribe`, {}, {
      withCredentials: true
    });
  }

  searchUsers(username: string) {
    return this.http.get<any[]>(`${this.baseUrl}users/search?username=${encodeURIComponent(username)}`, {
      withCredentials: true
    });
  }

  updateUserProfile(userId: string, data: UpdateUserProfileRequest): Observable<any> {
    return this.http.put(`${this.baseUrl}users/${userId}`, data, {
      withCredentials: true
    });
  }

}
