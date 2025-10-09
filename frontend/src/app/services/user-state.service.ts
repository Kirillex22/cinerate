import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class UserStateService {
  private currentUserSubject = new BehaviorSubject<{ id: string | null, name: string | null }>({
    id: null,
    name: null
  });

  constructor() {
    this.loadInitialData();
  }

  private loadInitialData() {
    if (typeof localStorage !== 'undefined') {
      const id = localStorage.getItem('currentUserID');
      const name = localStorage.getItem('currentUserName');
      this.currentUserSubject.next({ id, name });
    }
  }

  setCurrentUser(id: string, name: string | null) {
    localStorage.setItem('currentUserID', id);
    localStorage.setItem('currentUserName', name ?? "");
    this.currentUserSubject.next({ id, name });
  }

  clearUser() {
    localStorage.removeItem('currentUserID');
    localStorage.removeItem('currentUserName');
    this.currentUserSubject.next({ id: null, name: null });
  }

  getCurrentUser() {
    return this.currentUserSubject.asObservable();
  }
}