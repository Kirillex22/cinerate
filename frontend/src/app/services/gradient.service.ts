import { Injectable } from '@angular/core';
import { Observable, switchMap } from 'rxjs';

@Injectable({
  providedIn: 'root'
})

export class GradientService {
  constructor() { }

  getRandomColor(): string {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  }
  
  getRandomGradient(): string {
    const color1 = this.getRandomColor();
    const color2 = this.getRandomColor();
    return `linear-gradient(135deg, ${color1}, ${color2})`;
  }

}