import { Component } from '@angular/core';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { PlaylistService } from '../services/playlist.service';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { FormsModule } from '@angular/forms';
import { COUNTRY_LIST, GENRE_LIST } from '../models/config';

@Component({
  selector: 'app-playlist-generate-dialog',
  standalone: true,
  imports: [
    CommonModule, MatDialogModule, ReactiveFormsModule,
    MatFormFieldModule, MatInputModule, MatCheckboxModule,
    FormsModule
  ],
  templateUrl: './playlist-generate-dialog.component.html',
  styleUrls: ['./playlist-generate-dialog.component.css']
})
export class PlaylistGenerateDialogComponent {
  form: FormGroup;
  loading = false;
  errorMsg: string | null = null;

  genreInput = '';
  countryInput = '';
  genresList = GENRE_LIST;
  countryList = COUNTRY_LIST;

  constructor(
    private dialogRef: MatDialogRef<PlaylistGenerateDialogComponent>,
    private playlistService: PlaylistService,
    private fb: FormBuilder
  ) {
    this.form = this.fb.group({
      name: ['', Validators.required],
      description: [''],
      is_public: [true],
      gen_attrs: this.fb.group({
        name: [''],
        person: [''],
        genres: [[]],
        countries: [[]],
        year: this.fb.group({ lower: [''], upper: [''] }),
        kp_rating: this.fb.group({ lower: [''], upper: [''] }),
        length: this.fb.group({ lower: [''], upper: [''] }),
        age_rating: this.fb.group({ lower: [''], upper: [''] }),
        is_series: [undefined],
        user_rating: this.fb.group({
          storyline: [''],
          music: [''],
          montage: [''],
          acting_game: [''],
          atmosphere: [''],
          originality: ['']
        })
      })
    });
  }

  get genAttrsGroup(): FormGroup {
    return this.form.get('gen_attrs') as FormGroup;
  }

  get userRatingGroup(): FormGroup {
    return this.genAttrsGroup.get('user_rating') as FormGroup;
  }

  getGroup(name: string): FormGroup {
    return this.genAttrsGroup.get(name) as FormGroup;
  }

  addGenre() {
    const genres = this.genAttrsGroup.get('genres')!.value as string[];
    if (this.genreInput && !genres.includes(this.genreInput)) {
      this.genAttrsGroup.get('genres')!.setValue([...genres, this.genreInput]);
      this.genreInput = '';
    }
  }

  removeGenre(genre: string) {
    const genres = this.genAttrsGroup.get('genres')!.value as string[];
    this.genAttrsGroup.get('genres')!.setValue(genres.filter((g: string) => g !== genre));
  }

  addCountry() {
    const countries = this.genAttrsGroup.get('countries')!.value as string[];
    if (this.countryInput && !countries.includes(this.countryInput)) {
      this.genAttrsGroup.get('countries')!.setValue([...countries, this.countryInput]);
      this.countryInput = '';
    }
  }

  removeCountry(country: string) {
    const countries = this.genAttrsGroup.get('countries')!.value as string[];
    this.genAttrsGroup.get('countries')!.setValue(countries.filter((c: string) => c !== country));
  }

  generatePlaylist() {
    if (this.form.invalid) return;
    this.loading = true;
    this.errorMsg = null;
    const { name, description, is_public } = this.form.value;
    const gen_attrs_raw = this.form.value.gen_attrs;

    function parseRange(group: any) {
      const lower = group.lower !== '' && group.lower !== null && group.lower !== undefined ? Number(group.lower) : undefined;
      const upper = group.upper !== '' && group.upper !== null && group.upper !== undefined ? Number(group.upper) : undefined;
      if (lower === undefined && upper === undefined) return undefined;
      return { lower, upper };
    }

    // user_rating: если все поля пустые — undefined, иначе только заполненные
    let user_rating: any = undefined;
    if (gen_attrs_raw.user_rating) {
      const ur: any = {};
      let hasAny = false;
      for (const key of Object.keys(gen_attrs_raw.user_rating)) {
        const val = gen_attrs_raw.user_rating[key];
        if (val !== '' && val !== null && val !== undefined) {
          ur[key] = Number(val);
          hasAny = true;
        }
      }
      if (hasAny) user_rating = ur;
    }

    const gen_attrs: any = {};
    if (gen_attrs_raw.name) gen_attrs.name = gen_attrs_raw.name || undefined;
    if (gen_attrs_raw.person) gen_attrs.person = gen_attrs_raw.person || undefined;
    if (gen_attrs_raw.genres && gen_attrs_raw.genres.length > 0) gen_attrs.genres = gen_attrs_raw.genres;
    if (gen_attrs_raw.countries && gen_attrs_raw.countries.length > 0) gen_attrs.countries = gen_attrs_raw.countries;
    const year = parseRange(gen_attrs_raw.year);
    if (year) gen_attrs.year = year;
    const kp_rating = parseRange(gen_attrs_raw.kp_rating);
    if (kp_rating) gen_attrs.kp_rating = kp_rating;
    const length = parseRange(gen_attrs_raw.length);
    if (length) gen_attrs.length = length;
    const age_rating = parseRange(gen_attrs_raw.age_rating);
    if (age_rating) gen_attrs.age_rating = age_rating;
    if (gen_attrs_raw.is_series !== undefined) gen_attrs.is_series = gen_attrs_raw.is_series;
    if (user_rating) gen_attrs.user_rating = user_rating;

    console.log('gen_attrs:', gen_attrs); 

    this.playlistService.generatePlaylist(name, description, is_public, gen_attrs).subscribe({
      next: () => this.dialogRef.close({ created: true }),
      error: () => {
        this.errorMsg = 'Ошибка при генерации плейлиста';
        this.loading = false;
      }
    });
  }

  onCancel() {
    this.dialogRef.close();
  }
} 