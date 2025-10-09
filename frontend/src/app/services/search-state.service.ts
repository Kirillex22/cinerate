import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class SearchStateService {
  searchParams: any = null;
  films: any[] = [];
  isExternal = false;
  isFireShow = false;
}