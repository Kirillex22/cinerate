import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SubcribersPageComponent } from './subcribers-page.component';

describe('SubcribersPageComponent', () => {
  let component: SubcribersPageComponent;
  let fixture: ComponentFixture<SubcribersPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SubcribersPageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SubcribersPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
