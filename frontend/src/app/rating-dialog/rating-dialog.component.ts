import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-rating-dialog',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './rating-dialog.component.html',
  styleUrls: ['./rating-dialog.component.css']
})
export class RatingDialogComponent {
  characteristics = [
    { key: 'acting_game', label: 'Актёрская игра' },
    { key: 'atmosphere', label: 'Атмосфера' },
    { key: 'montage', label: 'Монтаж' },
    { key: 'music', label: 'Музыка' },
    { key: 'originality', label: 'Оригинальность' },
    { key: 'storyline', label: 'Сюжет' },
  ];
  ratingWords = ['Плохо', 'Нормально', 'Хорошо', 'Отлично'];
  ratings: { [key: string]: number } = {};

  constructor(
    public dialogRef: MatDialogRef<RatingDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    if (data && data.ratings) {
      this.ratings = {};
      for (const key of Object.keys(data.ratings)) {
        this.ratings[key] = Number(data.ratings[key]);
      }
    }
  }

  setRating(key: string, value: number) {
    this.ratings[key] = value;
  }

  onSave() {
    this.dialogRef.close(this.ratings);
  }

  onCancel() {
    this.dialogRef.close();
  }
}