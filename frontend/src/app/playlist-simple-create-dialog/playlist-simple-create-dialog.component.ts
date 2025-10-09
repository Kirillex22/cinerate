import { Component } from '@angular/core';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { PlaylistService } from '../services/playlist.service';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatCheckboxModule } from '@angular/material/checkbox';

@Component({
  selector: 'app-playlist-simple-create-dialog',
  imports: [CommonModule, MatDialogModule,  ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatCheckboxModule],
  templateUrl: './playlist-simple-create-dialog.component.html',
  styleUrls: ['./playlist-simple-create-dialog.component.css']
})
export class CreateSimplePlaylistDialogComponent {
  form: FormGroup;
  loading = false;
  errorMsg: string | null = null;

  constructor(
    private dialogRef: MatDialogRef<CreateSimplePlaylistDialogComponent>,
    private playlistService: PlaylistService,
    private fb: FormBuilder
  ) {
    this.form = this.fb.group({
      name: ['', Validators.required],
      description: [''],
      is_public: [true]
    });
  }

  createPlaylist() {
    if (this.form.invalid) return;
    this.loading = true;
    this.errorMsg = null;
    this.playlistService.createSimplePlaylist(
      this.form.value.name,
      this.form.value.description,
      this.form.value.is_public
    ).subscribe({
      next: () => this.dialogRef.close({ created: true }),
      error: () => {
        this.errorMsg = 'Ошибка при создании плейлиста';
        this.loading = false;
      }
    });
  }

  onSave() {
    this.dialogRef.close(this.form);
  }

  onCancel() {
    this.dialogRef.close();
  }
}