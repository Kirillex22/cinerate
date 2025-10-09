import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UpdateUserProfileDialogComponent } from './update-user-profile-dialog.component';

describe('UpdateUserProfileDialogComponent', () => {
  let component: UpdateUserProfileDialogComponent;
  let fixture: ComponentFixture<UpdateUserProfileDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UpdateUserProfileDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UpdateUserProfileDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
